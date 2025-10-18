#!/usr/bin/env python3
"""
PKI Key Generation Utility
AI Agent Governance Framework v2.1
Control: G-02 (Approval Enforcement - PKI)

Purpose: Generate RSA key pairs for signing Jira CR approvals
         Enables cryptographic proof of approval authority

Usage:
  Generate new key pair:
    python3 generate-pki-keys.py --name "Change Manager" --output-dir ./pki-keys

  Generate with specific key size:
    python3 generate-pki-keys.py --name "Security Lead" --key-size 4096 --output-dir ./pki-keys

  Sign a Jira CR approval:
    python3 generate-pki-keys.py --sign --cr-id CR-2025-1042 --private-key ./pki-keys/change-manager.key

Output:
  - <name>.key  (Private key - KEEP SECURE)
  - <name>.pub  (Public key - share for verification)
  - <name>.crt  (Self-signed certificate - for validation)

Security Notes:
  - Private keys are encrypted with AES-256
  - Store private keys in secrets manager (AWS Secrets Manager, HashiCorp Vault)
  - Rotate keys every 90 days minimum
  - Use hardware security modules (HSM) for production
"""

import os
import sys
import json
import base64
import getpass
from datetime import datetime, timedelta
from typing import Optional

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    from cryptography import x509
    from cryptography.x509.oid import NameOID
except ImportError:
    print("ERROR: cryptography library not installed")
    print("Install with: pip install cryptography")
    sys.exit(1)


class PKIKeyGenerator:
    """Generate and manage PKI keys for CR approval signing"""

    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.backend = default_backend()

    def generate_key_pair(self) -> rsa.RSAPrivateKey:
        """Generate RSA private key"""
        print(f"Generating {self.key_size}-bit RSA key pair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=self.backend
        )
        print("✅ Key pair generated")
        return private_key

    def generate_certificate(self, private_key: rsa.RSAPrivateKey,
                           common_name: str,
                           organization: str = "AI Agent Governance",
                           validity_days: int = 365) -> x509.Certificate:
        """Generate self-signed certificate"""
        print(f"Generating self-signed certificate (valid for {validity_days} days)...")

        # Build subject and issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        # Build certificate
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(f"{common_name.lower().replace(' ', '-')}.local"),
                ]),
                critical=False,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(private_key, hashes.SHA256(), self.backend)
        )

        print("✅ Certificate generated")
        return cert

    def save_private_key(self, private_key: rsa.RSAPrivateKey,
                        filepath: str,
                        password: Optional[str] = None):
        """Save private key to file (encrypted if password provided)"""
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())
            print(f"Saving encrypted private key to {filepath}...")
        else:
            encryption = serialization.NoEncryption()
            print(f"⚠️  WARNING: Saving unencrypted private key to {filepath}")
            print("   Consider using a password for production keys!")

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )

        with open(filepath, 'wb') as f:
            f.write(pem)

        # Set restrictive permissions
        os.chmod(filepath, 0o600)
        print(f"✅ Private key saved with permissions 600")

    def save_public_key(self, private_key: rsa.RSAPrivateKey, filepath: str):
        """Save public key to file"""
        print(f"Saving public key to {filepath}...")

        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(filepath, 'wb') as f:
            f.write(pem)

        print("✅ Public key saved")

    def save_certificate(self, cert: x509.Certificate, filepath: str):
        """Save certificate to file"""
        print(f"Saving certificate to {filepath}...")

        pem = cert.public_bytes(serialization.Encoding.PEM)

        with open(filepath, 'wb') as f:
            f.write(pem)

        print("✅ Certificate saved")

    def sign_cr_approval(self, cr_id: str, private_key_path: str,
                        password: Optional[str] = None) -> dict:
        """Sign a Jira CR approval with private key"""
        print(f"\nSigning Jira CR approval: {cr_id}")

        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key_pem = f.read()

        if password:
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=password.encode(),
                backend=self.backend
            )
        else:
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=self.backend
            )

        # Create approval data
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        approval_data = {
            'cr_id': cr_id,
            'status': 'Approved',
            'timestamp': timestamp,
            'signer_role': 'Change Manager'
        }

        # Sign the data
        data_string = json.dumps(approval_data, sort_keys=True)
        signature = private_key.sign(
            data_string.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Load certificate for signer info
        cert_path = private_key_path.replace('.key', '.crt')
        if os.path.exists(cert_path):
            with open(cert_path, 'rb') as f:
                cert = x509.load_pem_x509_certificate(f.read(), self.backend)
            signer_cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        else:
            signer_cn = "Unknown"

        # Build signature payload
        signature_payload = {
            'signature': base64.b64encode(signature).decode(),
            'signed_data': data_string,
            'signer_certificate': base64.b64encode(
                private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            ).decode(),
            'timestamp': timestamp,
            'algorithm': 'RSA-SHA256',
            'signer': signer_cn
        }

        print(f"✅ CR {cr_id} signed successfully")
        print(f"   Signer: {signer_cn}")
        print(f"   Timestamp: {timestamp}")

        return signature_payload


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PKI Key Generation for Jira CR Approvals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate keys for Change Manager
  python3 generate-pki-keys.py --name "Change Manager" --output-dir ./pki-keys

  # Generate keys with 4096-bit strength
  python3 generate-pki-keys.py --name "Security Lead" --key-size 4096

  # Sign a CR approval
  python3 generate-pki-keys.py --sign --cr-id CR-2025-1042 --private-key ./pki-keys/change-manager.key

  # Sign with encrypted key
  python3 generate-pki-keys.py --sign --cr-id CR-2025-1042 --private-key ./pki-keys/change-manager.key --password

Security Best Practices:
  1. Store private keys in a secrets manager (AWS Secrets Manager, HashiCorp Vault)
  2. Use hardware security modules (HSM) for production
  3. Rotate keys every 90 days
  4. Never commit private keys to version control
  5. Use strong passwords (minimum 16 characters)
        """
    )

    parser.add_argument('--name', type=str, help='Common Name for certificate (e.g., "Change Manager")')
    parser.add_argument('--output-dir', type=str, default='./pki-keys', help='Output directory for keys')
    parser.add_argument('--key-size', type=int, choices=[2048, 3072, 4096], default=2048,
                       help='RSA key size in bits (default: 2048)')
    parser.add_argument('--organization', type=str, default='AI Agent Governance',
                       help='Organization name for certificate')
    parser.add_argument('--validity-days', type=int, default=365,
                       help='Certificate validity period in days (default: 365)')
    parser.add_argument('--no-password', action='store_true',
                       help='Do not encrypt private key (NOT RECOMMENDED)')

    # Signing options
    parser.add_argument('--sign', action='store_true', help='Sign a Jira CR approval')
    parser.add_argument('--cr-id', type=str, help='Jira CR ID to sign (e.g., CR-2025-1042)')
    parser.add_argument('--private-key', type=str, help='Path to private key for signing')
    parser.add_argument('--password', action='store_true', help='Prompt for private key password')

    args = parser.parse_args()

    generator = PKIKeyGenerator(key_size=args.key_size)

    # Signing mode
    if args.sign:
        if not args.cr_id or not args.private_key:
            print("ERROR: --cr-id and --private-key required for signing")
            sys.exit(1)

        password = None
        if args.password:
            password = getpass.getpass("Enter private key password: ")

        signature_payload = generator.sign_cr_approval(args.cr_id, args.private_key, password)

        # Save signature to file
        output_file = f"{args.cr_id}-signature.json"
        with open(output_file, 'w') as f:
            json.dump(signature_payload, f, indent=2)

        print(f"\n✅ Signature saved to: {output_file}")
        print("\nAdd this signature to your Jira CR custom field 'PKI Signature'")
        sys.exit(0)

    # Key generation mode
    if not args.name:
        print("ERROR: --name required for key generation")
        print("Example: --name \"Change Manager\"")
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate filename-safe name
    safe_name = args.name.lower().replace(' ', '-').replace('_', '-')
    private_key_path = os.path.join(args.output_dir, f"{safe_name}.key")
    public_key_path = os.path.join(args.output_dir, f"{safe_name}.pub")
    cert_path = os.path.join(args.output_dir, f"{safe_name}.crt")

    print("=" * 60)
    print("PKI Key Generation - AI Agent Governance Framework")
    print("=" * 60)
    print(f"Common Name:     {args.name}")
    print(f"Organization:    {args.organization}")
    print(f"Key Size:        {args.key_size} bits")
    print(f"Validity:        {args.validity_days} days")
    print(f"Output Dir:      {args.output_dir}")
    print("=" * 60)
    print()

    # Get password if needed
    password = None
    if not args.no_password:
        password = getpass.getpass("Enter password to encrypt private key (min 8 chars): ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("ERROR: Passwords do not match")
            sys.exit(1)

        if len(password) < 8:
            print("ERROR: Password must be at least 8 characters")
            sys.exit(1)

    # Generate keys
    private_key = generator.generate_key_pair()

    # Generate certificate
    cert = generator.generate_certificate(
        private_key,
        args.name,
        args.organization,
        args.validity_days
    )

    # Save files
    generator.save_private_key(private_key, private_key_path, password)
    generator.save_public_key(private_key, public_key_path)
    generator.save_certificate(cert, cert_path)

    # Print summary
    print("\n" + "=" * 60)
    print("✅ PKI Keys Generated Successfully")
    print("=" * 60)
    print(f"Private Key:     {private_key_path}")
    print(f"Public Key:      {public_key_path}")
    print(f"Certificate:     {cert_path}")
    print()
    print("⚠️  SECURITY WARNING:")
    print(f"   - KEEP {private_key_path} SECURE")
    print("   - Store in secrets manager (AWS Secrets Manager, Vault)")
    print("   - Never commit to version control")
    print("   - Rotate every 90 days minimum")
    print()
    print("Next Steps:")
    print(f"   1. Store private key in secrets manager")
    print(f"   2. Share {public_key_path} with validators")
    print(f"   3. Add {cert_path} to Jira CR approval workflow")
    print("   4. Use --sign to create approval signatures")
    print()
    print("Example signing command:")
    print(f"   python3 generate-pki-keys.py --sign --cr-id CR-2025-1042 \\")
    print(f"     --private-key {private_key_path} --password")
    print("=" * 60)


if __name__ == '__main__':
    main()
