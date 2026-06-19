# Conjur Access Control Policy
# Standard: NIST SP 800-53 IA-5 (Authenticator Management)
# Defines agent service account hosts and maps access to LLM credentials.

- !policy
  id: ai-agents-prod
  body:
    # 1. Define hosts for each K8s ServiceAccount identity
    - !host security-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: security-agent
        authn-k8s/image-hash: "sha256:7bbcf53761cc20f92479f67a216db8a1f681cfc84305bc5be95759bc7e828d57"

    - !host it-ops-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: it-ops-agent

    - !host ai-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: ai-agent

    - !host architect-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: architect-agent

    # 2. Define the secrets variables
    - !variable secrets/gpis-jwt-secret
    - !variable secrets/llm-api-key
    - !variable secrets/database-credentials

    # 3. Create consumer group and add members
    - !group governance-consumers
    
    - !grant
      role: !group governance-consumers
      members:
        - !host security-agent
        - !host it-ops-agent
        - !host ai-agent
        - !host architect-agent

    # 4. Grant read permissions on variables to consumer group
    - !permit
      role: !group governance-consumers
      privileges: [ read ]
      resources:
        - !variable secrets/gpis-jwt-secret
        - !variable secrets/llm-api-key
        - !variable secrets/database-credentials
