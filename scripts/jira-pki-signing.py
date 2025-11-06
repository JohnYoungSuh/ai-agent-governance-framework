#!/usr/bin/env python3
"""
Jira PKI Signing for Multi-Party Approvals
AI Agent Governance Framework v2.1
Control: G-07 (Jira Integration), APP-001 (Human Primacy)

Purpose: Cryptographic signing of Jira CR approvals for non-repudiation
         Enables multi-party approval verification with PKI

Usage:
  # Sign an approval
  python3 jira-pki-signing.py sign --cr-id CR-2024-0001 \
      --approver "john.doe@example.com" \
      --private-key /path/to/private.pem

  # Verify approval signatures
  python3 jira-pki-signing.py verify --cr-id CR-2024-0001 \
      --public-keys-dir /path/to/public-keys

  # Generate key pair
  python3 jira-pki-signing.py generate-keys --email "john.doe@example.com" \
      --output-dir /path/to/keys

Environment Variables:
  PKI_KEYS_DIR        - Directory containing PKI keys
  JIRA_URL           - Jira instance URL
  JIRA_API_TOKEN     - Jira API token for updating custom fields

Exit Codes:
  0 - Success
  1 - Configuration error
  2 - Cryptographic operation failed
  3 - Verification failed
"""

import os
import sys
import json
import hashlib
import base64
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    from cryptography import x509
    from cryptography.x509.oid import NameOID
except ImportError:
    print("ERROR: cryptography library not installed", file=sys.stderr)
    print("Install with: pip install cryptography", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraPKISigner:
    """Handle PKI signing operations for Jira CR approvals"""

    def __init__(self, keys_dir: str):
        """Initialize PKI signer with keys directory"""
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

    def generate_key_pair(self, email: str, name: str = "") -> Tuple[str, str]:
        """
        Generate RSA key pair for an approver

        Returns:
            (private_key_path, public_key_path)
        """
        logger.info(f"Generating RSA-4096 key pair for {email}")

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        # Generate public key
        public_key = private_key.public_key()

        # Serialize private key (encrypted with password)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # For automation
        )

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Save keys
        email_safe = email.replace('@', '_at_').replace('.', '_')
        private_path = self.keys_dir / f"{email_safe}_private.pem"
        public_path = self.keys_dir / f"{email_safe}_public.pem"

        with open(private_path, 'wb') as f:
            f.write(private_pem)
        os.chmod(private_path, 0o600)  # Owner read/write only

        with open(public_path, 'wb') as f:
            f.write(public_pem)

        logger.info(f"Keys generated: {private_path}, {public_path}")
        return str(private_path), str(public_path)

    def sign_approval(self, cr_id: str, approver: str, private_key_path: str,
                     approval_data: Dict) -> Dict:
        """
        Sign a CR approval with approver's private key

        Args:
            cr_id: Jira CR ID (e.g., CR-2024-0001)
            approver: Approver email
            private_key_path: Path to private key PEM file
            approval_data: Additional approval data to sign

        Returns:
            Signature object with metadata
        """
        logger.info(f"Signing approval for {cr_id} by {approver}")

        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

        # Build approval document
        timestamp = datetime.utcnow().isoformat() + 'Z'
        approval_doc = {
            'cr_id': cr_id,
            'approver': approver,
            'timestamp': timestamp,
            'approval_data': approval_data
        }

        # Serialize for signing (deterministic JSON)
        approval_json = json.dumps(approval_doc, sort_keys=True, separators=(',', ':'))
        approval_bytes = approval_json.encode('utf-8')

        # Generate SHA-256 hash
        doc_hash = hashlib.sha256(approval_bytes).hexdigest()

        # Sign with RSA-PSS
        signature = private_key.sign(
            approval_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode signature to base64
        signature_b64 = base64.b64encode(signature).decode('ascii')

        # Build signature object
        signature_obj = {
            'cr_id': cr_id,
            'approver': approver,
            'timestamp': timestamp,
            'document_hash': doc_hash,
            'signature': signature_b64,
            'algorithm': 'RSA-PSS-SHA256',
            'key_size': 4096,
            'approval_data': approval_data
        }

        # Save signature
        sig_path = self.keys_dir / f"{cr_id}_{approver.replace('@', '_at_')}_signature.json"
        with open(sig_path, 'w') as f:
            json.dump(signature_obj, f, indent=2)

        logger.info(f"Signature saved: {sig_path}")
        return signature_obj

    def verify_approval(self, signature_obj: Dict, public_key_path: str) -> bool:
        """
        Verify a CR approval signature

        Args:
            signature_obj: Signature object from sign_approval()
            public_key_path: Path to approver's public key

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            logger.info(f"Verifying signature for {signature_obj['cr_id']} by {signature_obj['approver']}")

            # Load public key
            with open(public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )

            # Reconstruct approval document
            approval_doc = {
                'cr_id': signature_obj['cr_id'],
                'approver': signature_obj['approver'],
                'timestamp': signature_obj['timestamp'],
                'approval_data': signature_obj['approval_data']
            }

            approval_json = json.dumps(approval_doc, sort_keys=True, separators=(',', ':'))
            approval_bytes = approval_json.encode('utf-8')

            # Verify hash
            doc_hash = hashlib.sha256(approval_bytes).hexdigest()
            if doc_hash != signature_obj['document_hash']:
                logger.error("Document hash mismatch")
                return False

            # Decode signature
            signature = base64.b64decode(signature_obj['signature'])

            # Verify signature
            public_key.verify(
                signature,
                approval_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            logger.info("✅ Signature verification PASSED")
            return True

        except Exception as e:
            logger.error(f"❌ Signature verification FAILED: {str(e)}")
            return False

    def verify_multi_party_approval(self, cr_id: str, required_approvers: List[str],
                                   public_keys_dir: str) -> Dict:
        """
        Verify multi-party approval for a CR

        Args:
            cr_id: Jira CR ID
            required_approvers: List of required approver emails
            public_keys_dir: Directory containing public keys

        Returns:
            Verification results with status for each approver
        """
        logger.info(f"Verifying multi-party approval for {cr_id}")

        results = {
            'cr_id': cr_id,
            'required_approvers': required_approvers,
            'verification_timestamp': datetime.utcnow().isoformat() + 'Z',
            'approvers': {},
            'overall_status': 'PENDING'
        }

        keys_dir = Path(public_keys_dir)
        valid_count = 0

        for approver in required_approvers:
            email_safe = approver.replace('@', '_at_').replace('.', '_')

            # Find signature file
            sig_pattern = f"{cr_id}_{email_safe}_signature.json"
            sig_path = self.keys_dir / sig_pattern

            # Find public key
            public_key_path = keys_dir / f"{email_safe}_public.pem"

            if not sig_path.exists():
                results['approvers'][approver] = {
                    'status': 'MISSING',
                    'error': 'Signature not found'
                }
                continue

            if not public_key_path.exists():
                results['approvers'][approver] = {
                    'status': 'ERROR',
                    'error': 'Public key not found'
                }
                continue

            # Load and verify signature
            try:
                with open(sig_path, 'r') as f:
                    signature_obj = json.load(f)

                if self.verify_approval(signature_obj, str(public_key_path)):
                    results['approvers'][approver] = {
                        'status': 'VALID',
                        'timestamp': signature_obj['timestamp'],
                        'document_hash': signature_obj['document_hash']
                    }
                    valid_count += 1
                else:
                    results['approvers'][approver] = {
                        'status': 'INVALID',
                        'error': 'Signature verification failed'
                    }
            except Exception as e:
                results['approvers'][approver] = {
                    'status': 'ERROR',
                    'error': str(e)
                }

        # Determine overall status
        if valid_count == len(required_approvers):
            results['overall_status'] = 'APPROVED'
        elif valid_count > 0:
            results['overall_status'] = 'PARTIAL'
        else:
            results['overall_status'] = 'REJECTED'

        logger.info(f"Multi-party verification: {valid_count}/{len(required_approvers)} valid")
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PKI signing for Jira CR multi-party approvals'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate keys command
    gen_parser = subparsers.add_parser('generate-keys', help='Generate RSA key pair')
    gen_parser.add_argument('--email', required=True, help='Approver email')
    gen_parser.add_argument('--name', default='', help='Approver name')
    gen_parser.add_argument('--output-dir', required=True, help='Output directory for keys')

    # Sign command
    sign_parser = subparsers.add_parser('sign', help='Sign CR approval')
    sign_parser.add_argument('--cr-id', required=True, help='Jira CR ID')
    sign_parser.add_argument('--approver', required=True, help='Approver email')
    sign_parser.add_argument('--private-key', required=True, help='Path to private key')
    sign_parser.add_argument('--approval-status', default='Approved', help='Approval status')
    sign_parser.add_argument('--comments', default='', help='Approval comments')
    sign_parser.add_argument('--keys-dir', default='./pki-keys', help='PKI keys directory')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify CR approval signatures')
    verify_parser.add_argument('--cr-id', required=True, help='Jira CR ID')
    verify_parser.add_argument('--required-approvers', required=True, nargs='+',
                              help='Required approver emails')
    verify_parser.add_argument('--public-keys-dir', required=True,
                              help='Directory with public keys')
    verify_parser.add_argument('--keys-dir', default='./pki-keys', help='PKI keys directory')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'generate-keys':
            signer = JiraPKISigner(args.output_dir)
            private_path, public_path = signer.generate_key_pair(args.email, args.name)
            print(f"✅ Key pair generated successfully")
            print(f"Private key: {private_path}")
            print(f"Public key: {public_path}")
            print(f"\n⚠️  IMPORTANT: Keep private key secure and never commit to git!")

        elif args.command == 'sign':
            signer = JiraPKISigner(args.keys_dir)
            approval_data = {
                'status': args.approval_status,
                'comments': args.comments
            }
            signature_obj = signer.sign_approval(
                args.cr_id,
                args.approver,
                args.private_key,
                approval_data
            )
            print(f"✅ Approval signed successfully")
            print(f"CR ID: {signature_obj['cr_id']}")
            print(f"Approver: {signature_obj['approver']}")
            print(f"Timestamp: {signature_obj['timestamp']}")
            print(f"Document Hash: {signature_obj['document_hash'][:16]}...")

        elif args.command == 'verify':
            signer = JiraPKISigner(args.keys_dir)
            results = signer.verify_multi_party_approval(
                args.cr_id,
                args.required_approvers,
                args.public_keys_dir
            )

            print(f"\n{'='*60}")
            print(f"Multi-Party Approval Verification Results")
            print(f"{'='*60}")
            print(f"CR ID: {results['cr_id']}")
            print(f"Overall Status: {results['overall_status']}")
            print(f"Verification Time: {results['verification_timestamp']}")
            print(f"\nApprover Status:")

            for approver, status in results['approvers'].items():
                emoji = '✅' if status['status'] == 'VALID' else '❌'
                print(f"  {emoji} {approver}: {status['status']}")
                if 'error' in status:
                    print(f"     Error: {status['error']}")
                if 'timestamp' in status:
                    print(f"     Signed: {status['timestamp']}")

            # Exit with non-zero if not fully approved
            if results['overall_status'] != 'APPROVED':
                sys.exit(3)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(2)


if __name__ == '__main__':
    main()
