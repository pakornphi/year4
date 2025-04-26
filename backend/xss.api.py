import requests
import json

# --- Simulated API scanning functions ---
def scan_zap(target_url):
    """
    Simulated function to scan using OWASP ZAP API.
    In a real implementation, you would call ZAP's REST API and parse the results.
    """
    print("[*] Scanning with OWASP ZAP API...")
    # Simulated response data
    results = [
        {"type": "XSS", "detail": "Reflected XSS found in parameter 'q'"},
        {"type": "SQL Injection", "detail": "SQL Injection in parameter 'id'"}
    ]
    # Filter only XSS vulnerabilities
    return [v for v in results if v["type"] == "XSS"]

def scan_burp(target_url):
    """
    Simulated function to scan using Burp Suite API.
    """
    print("[*] Scanning with Burp Suite API...")
    results = [
        {"type": "XSS", "detail": "Stored XSS found in comment field"},
        {"type": "XSS", "detail": "Reflected XSS in HTTP header"}
    ]
    return [v for v in results if v["type"] == "XSS"]

def scan_arachni(target_url):
    """
    Simulated function to scan using Arachni API.
    """
    print("[*] Scanning with Arachni API...")
    results = [
        {"type": "XSS", "detail": "DOM-based XSS in parameter 'dom'"},
        {"type": "Info", "detail": "Server banner detected"}
    ]
    return [v for v in results if v["type"] == "XSS"]

def scan_acunetix(target_url):
    """
    Simulated function to scan using Acunetix API.
    """
    print("[*] Scanning with Acunetix API...")
    results = [
        {"type": "XSS", "detail": "Reflected XSS in search input"},
        {"type": "Directory Listing", "detail": "Directory listing vulnerability"}
    ]
    return [v for v in results if v["type"] == "XSS"]

def scan_netsparker(target_url):
    """
    Simulated function to scan using Netsparker API.
    """
    print("[*] Scanning with Netsparker API...")
    results = [
        {"type": "XSS", "detail": "Stored XSS in user profile page"},
        {"type": "CSRF", "detail": "Missing CSRF token on form"}
    ]
    return [v for v in results if v["type"] == "XSS"]

# --- Main function to aggregate XSS results from all APIs ---
def main():
    target_url = "http://example.com"  # Replace with your target URL
    all_xss_results = []

    # Call each API scan function and aggregate only XSS vulnerabilities.
    all_xss_results.extend(scan_zap(target_url))
    all_xss_results.extend(scan_burp(target_url))
    all_xss_results.extend(scan_arachni(target_url))
    all_xss_results.extend(scan_acunetix(target_url))
    all_xss_results.extend(scan_netsparker(target_url))

    # Print only XSS vulnerability details
    print("\n[*] Aggregated XSS Vulnerabilities:")
    if not all_xss_results:
        print("No XSS vulnerabilities found.")
    else:
        for vulnerability in all_xss_results:
            print(f"- {vulnerability['detail']}")

if __name__ == "__main__":
    main()
