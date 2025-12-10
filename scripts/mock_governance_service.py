
import http.server
import socketserver
import json
import random

# Mock Governance Service
# Helper script to test the ask_governance.yml Ansible task

PORT = 8080

class GovernanceHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/v1/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                request = json.loads(post_data)
                print(f"Received governance request: {json.dumps(request, indent=2)}")
                
                # Mock Decision Logic
                context = request.get("context", {})
                risk_level = context.get("risk_level", "low")
                action = request.get("action", "")

                if "force_deny" in action:
                    response = {"decision": "DENY", "reason": "Administrative Lock"}
                elif risk_level == "high":
                    response = {"decision": "MANUAL_REVIEW", "reason": "High risk action detected", "task_id": f"TASK-{random.randint(1000,9999)}"}
                else:
                    response = {"decision": "APPROVE", "reason": "Standard automated approval"}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"Responded with: {response['decision']}")
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

print(f"Starting Mock Governance Service on port {PORT}...")
print("Endpoints:")
print(f"  POST http://localhost:{PORT}/api/v1/ask")
print("Press Ctrl+C to stop.")

with socketserver.TCPServer(("", PORT), GovernanceHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
