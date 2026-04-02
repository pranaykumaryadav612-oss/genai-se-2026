#!/usr/bin/env python3
"""
Test script to demonstrate the Jira AI Engine pipeline.
Run with: python test_pipeline.py
"""

from jira_ai_engine import run_pipeline
import json

# Sample Jira ticket for testing
SAMPLE_TICKET = """
Bug: Application crashes when user tries to upload a profile picture larger than 5MB

Description:
Users are reporting that the application crashes when they attempt to upload a profile picture 
that exceeds 5MB in size. This is causing a poor user experience and preventing users from 
setting their profile pictures.

Acceptance Criteria:
- Validate file size before upload (max 5MB)
- Show user-friendly error message if file is too large
- Support common image formats (JPG, PNG, GIF)
- Compress images if possible without quality loss
- Log upload attempts for monitoring

Priority: High
Component: User Profile Module
"""

# Project context for better AI decisions
PROJECT_CONTEXT = """
This is a React/Node.js web application with:
- Frontend: React with TypeScript, using Ant Design components
- Backend: Node.js with Express, MongoDB database
- File storage: AWS S3
- Image processing: Sharp library
- Current upload endpoint: POST /api/users/profile-picture
"""

def main():
    print("=" * 70)
    print(" JIRA AI ENGINE - TEST PIPELINE")
    print("=" * 70)
    print("\n📝 Sample Ticket:")
    print(SAMPLE_TICKET)
    print("\n" + "=" * 70)
    
    # Ask user if they want to create actual PR
    print("\n" + "=" * 70)
    choice = input("\n🔥 Create actual PR on GitHub? (y/n, default: n): ").strip().lower()
    dry_run = choice != 'y'
    
    if dry_run:
        print("\n🚀 Running pipeline in DRY-RUN mode (no PR will be created)...\n")
    else:
        print("\n🚀 Running pipeline in LIVE mode (WILL create PR on GitHub)...\n")
        print("⚠️  WARNING: This will create a real branch and PR on GitHub!")
        confirm = input("Are you sure? (yes to confirm): ").strip().lower()
        if confirm != 'yes':
            print("Aborted. Run again to create PR.")
            return None
    
    results = run_pipeline(
        ticket_text=SAMPLE_TICKET,
        project_context=PROJECT_CONTEXT,
        dry_run=dry_run
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print(" TEST RESULTS SUMMARY")
    print("=" * 70)
    
    if results.get("success"):
        print("\n✅ Pipeline completed successfully!")
        
        # Show parsed data summary
        parsing = results.get("stages", {}).get("parsing", {})
        print(f"\n📊 Parsed Ticket:")
        print(f"   Type: {parsing.get('type', 'N/A')}")
        print(f"   Title: {parsing.get('title', 'N/A')}")
        print(f"   Priority: {parsing.get('priority', 'N/A')}")
        
        # Show decision summary
        decision = results.get("stages", {}).get("decision", {})
        print(f"\n🎯 Decision:")
        print(f"   Ticket Type: {decision.get('ticket_type', 'N/A')}")
        print(f"   Action: {decision.get('action', 'N/A')}")
        print(f"   Approach: {decision.get('approach', 'N/A')}")
        
        # Show generation summary
        generation = results.get("stages", {}).get("generation", [])
        print(f"\n📝 Generated Files: {len(generation)}")
        for i, file_info in enumerate(generation, 1):
            print(f"   {i}. {file_info.get('filename', 'N/A')} ({file_info.get('template_used', 'N/A')})")
        
        print("\n🎉 Test completed! The pipeline is working correctly.")
        print("   (Dry run mode - no PR was created)")
        
    else:
        print("\n❌ Pipeline failed!")
        print(f"   Error: {results.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Optional: Save results to file for inspection
    save_results = input("\nSave detailed results to results.json? (y/n): ").strip().lower()
    if save_results == 'y':
        with open("results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("✅ Results saved to results.json")