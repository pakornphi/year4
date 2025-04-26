import requests
import subprocess
import time

# ===========================================
# OWASP ZAP API Integration (Focus on CSRF Issues)
# ===========================================
def zap_scan_csrf(target_url):
    zap_url = 'http://localhost:8080'  # ZAP running locally
    api_key = 'your_zap_api_key'

    # Start a scan
    start_url_scan = f"{zap_url}/JSON/ascan/action/scan?url={target_url}&apikey={api_key}"
    response = requests.get(start_url_scan)
    
    if response.status_code == 200:
        scan_id = response.json()['scanid']
        print(f"ZAP Scan Started with ID: {scan_id}")
        
        # Wait for scan to complete
        while True:
            status_url = f"{zap_url}/JSON/ascan/view/status?scanId={scan_id}&apikey={api_key}"
            status_response = requests.get(status_url)
            status = status_response.json()['status']
            if status == '100':
                print("ZAP Scan completed.")
                break
            time.sleep(5)  # Wait before checking again

        # Fetch CSRF-related issues after scan
        csrf_issues_url = f"{zap_url}/JSON/core/view/messages?url={target_url}&apikey={api_key}"
        issues_response = requests.get(csrf_issues_url)
        
        if issues_response.status_code == 200:
            issues = issues_response.json()['messages']
            csrf_issues = [issue for issue in issues if 'CSRF' in issue.get('alert', '').upper()]
            if csrf_issues:
                print("\nCSRF Issues Found by ZAP:")
                for issue in csrf_issues:
                    print(f"Alert: {issue['alert']}, URL: {issue['url']}")
            else:
                print("No CSRF issues found by ZAP.")
        else:
            print("Failed to fetch ZAP issues.")
    else:
        print("Failed to start ZAP scan.")
        
# ===========================================
# Burp Suite API Integration (Focus on CSRF Issues)
# ===========================================
def burp_scan_csrf(target_url):
    burp_url = 'http://localhost:1337'  # Burp Suite API proxy
    api_key = 'your_burp_api_key'

    # Initiate scan via Burp Suite API
    scan_url = f"{burp_url}/burp/api/scanner/scan?url={target_url}&apikey={api_key}"
    response = requests.get(scan_url)

    if response.status_code == 200:
        print("Burp Suite scan initiated.")
        # Fetch issues related to CSRF from Burp's API (assuming you're fetching issue reports)
        issues_url = f"{burp_url}/burp/api/issues?apikey={api_key}"
        issues_response = requests.get(issues_url)
        
        if issues_response.status_code == 200:
            issues = issues_response.json()
            csrf_issues = [issue for issue in issues if 'CSRF' in issue.get('name', '').upper()]
            if csrf_issues:
                print("\nCSRF Issues Found by Burp Suite:")
                for issue in csrf_issues:
                    print(f"Name: {issue['name']}, Severity: {issue['severity']}, URL: {issue['url']}")
            else:
                print("No CSRF issues found by Burp Suite.")
        else:
            print("Failed to fetch Burp Suite issues.")
    else:
        print("Failed to start Burp Suite scan.")

# ===========================================
# Nikto Scan (Focus on CSRF Issues)
# ===========================================
def nikto_scan(target_url):
    # Run Nikto command via subprocess
    command = f"nikto -h {target_url}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        # Filter Nikto output for CSRF-related findings
        output = stdout.decode()
        csrf_issues = [line for line in output.split('\n') if 'csrf' in line.lower()]
        
        if csrf_issues:
            print("\nCSRF Issues Found by Nikto:")
            for issue in csrf_issues:
                print(issue)
        else:
            print("No CSRF issues found by Nikto.")
    else:
        print(f"Nikto scan failed with error:\n{stderr.decode()}")

# ===========================================
# Main Function to Run All Scans
# ===========================================
def run_all_scans(target_url):
    print(f"\nRunning CSRF Scans on {target_url}...\n")
    
    # Run OWASP ZAP scan
    print("\nRunning OWASP ZAP Scan for CSRF...")
    zap_scan_csrf(target_url)
    
    # Run Burp Suite scan
    print("\nRunning Burp Suite Scan for CSRF...")
    burp_scan_csrf(target_url)

    # Run Nikto scan
    print("\nRunning Nikto Scan for CSRF...")
    nikto_scan(target_url)

# ===========================================
# Run the Scans (Replace with your target URL)
# ===========================================
if __name__ == '__main__':
    target_url = 'http://example.com'  # Replace with your target URL
    run_all_scans(target_url)
