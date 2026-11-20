"""Synthetic feedback evidence audit for an independent Enterpret hiring demo.
No model calls, customer data or Enterpret integration. python audit.py --test
"""
import argparse
import json
import unittest
from collections import Counter


def audit(records, claims, tenant):
    """Check citation integrity, not whether a claim is semantically true."""
    ids = [r.get('id') for r in records]
    duplicates = {k for k, n in Counter(ids).items() if n > 1}
    by_id = {r.get('id'): r for r in records}
    findings = []
    for index, claim in enumerate(claims):
        errors = []
        refs = claim.get('evidence', [])
        if not refs:
            errors.append('missing_evidence')
        seen = set()
        for ref in refs:
            key = ref.get('id')
            if key in seen:
                errors.append('repeated_citation')
            seen.add(key)
            if key in duplicates:
                errors.append('ambiguous_source_id')
                continue
            source = by_id.get(key)
            if source is None:
                errors.append('unknown_source')
                continue
            if source.get('tenant') != tenant:
                errors.append('cross_tenant_source')
                continue
            quote = ref.get('quote', '')
            if not isinstance(quote, str) or not quote.strip():
                errors.append('empty_quote')
            elif quote not in source.get('text', ''):
                errors.append('quote_not_found')
        findings.append({'claim_index': index, 'status': 'review' if errors else 'citation_checks_pass',
                         'errors': sorted(set(errors))})
    return findings


RECORDS = [
    {'id': 'ticket-1', 'tenant': 'demo', 'text': 'Search is slow on large workspaces.'},
    {'id': 'review-2', 'tenant': 'demo', 'text': 'I cannot filter search results by project.'},
    {'id': 'ticket-3', 'tenant': 'other', 'text': 'Export failed.'},
]
CLAIMS = [
    {'text': 'Search performance needs attention.', 'evidence': [
        {'id': 'ticket-1', 'quote': 'Search is slow'}]},
    {'text': 'Export is the main demo-tenant issue.', 'evidence': [
        {'id': 'ticket-3', 'quote': 'Export failed.'}]},
    {'text': 'Users demand dark mode.', 'evidence': [
        {'id': 'review-2', 'quote': 'Please add dark mode'}]},
]


class AuditTests(unittest.TestCase):
    def run_case(self, evidence, records=None):
        return audit(RECORDS if records is None else records,
                     [{'text': 'Synthetic claim', 'evidence': evidence}], 'demo')[0]

    def test_valid_quote(self):
        self.assertEqual(self.run_case([{'id': 'ticket-1', 'quote': 'Search is slow'}])['errors'], [])

    def test_missing_evidence(self):
        self.assertIn('missing_evidence', self.run_case([])['errors'])

    def test_unknown_id(self):
        self.assertIn('unknown_source', self.run_case([{'id': 'missing', 'quote': 'x'}])['errors'])

    def test_cross_tenant(self):
        self.assertIn('cross_tenant_source', self.run_case([{'id': 'ticket-3', 'quote': 'Export failed.'}])['errors'])

    def test_invented_quote(self):
        self.assertIn('quote_not_found', self.run_case([{'id': 'ticket-1', 'quote': 'dark mode'}])['errors'])

    def test_blank_quote(self):
        self.assertIn('empty_quote', self.run_case([{'id': 'ticket-1', 'quote': ' '}])['errors'])

    def test_duplicate_source_id(self):
        self.assertIn('ambiguous_source_id', self.run_case([{'id': 'ticket-1', 'quote': 'Search'}], RECORDS + [RECORDS[0]])['errors'])

    def test_repeated_citation(self):
        ref = {'id': 'ticket-1', 'quote': 'Search'}
        self.assertIn('repeated_citation', self.run_case([ref, ref])['errors'])

    def test_empty_claims(self):
        self.assertEqual(audit(RECORDS, [], 'demo'), [])

    def test_semantics_are_not_certified(self):
        result = audit(RECORDS, [{'text': 'Unsupported causal conclusion', 'evidence': [
            {'id': 'ticket-1', 'quote': 'Search is slow'}]}], 'demo')[0]
        self.assertEqual(result['status'], 'citation_checks_pass')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    if args.test:
        unittest.main(argv=['audit.py'], verbosity=2)
    else:
        print(json.dumps(audit(RECORDS, CLAIMS, 'demo'), indent=2))
