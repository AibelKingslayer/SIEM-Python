🧠 What is SIEM?

SIEM stands for Security Information and Event Management. It is a system that collects, analyzes, and correlates security event data from various sources — like operating systems, applications, and network devices — in real time.

A SIEM helps:

🔍 Detect suspicious activity and threats

🧾 Maintain audit trails for compliance

🚨 Alert security teams about incidents

📊 Visualize security trends across systems

Traditional enterprise SIEMs (like Splunk, QRadar, or Microsoft Sentinel) are powerful but often complex and expensive.

🐍 My Lightweight Python SIEM

This project is a lightweight, beginner-friendly SIEM written in Python, focused specifically on Windows event monitoring. It covers high-value events such as:

✅ Successful and failed logins

👤 New user creation

🔑 Password changes/resets

📦 Application installations

🔌 USB device insertions

All critical events are parsed from the Windows Event Logs and pushed to a Discord channel using a webhook, so you can get real-time alerts without setting up a full SIEM stack.

🛠️ Technical Overview
The tool leverages Python's capabilities to interact with Windows Event Logs, utilizing modules such as pywin32 for event log access and requests for sending HTTP POST requests to Discord webhooks. By parsing relevant event IDs, the tool identifies specific security-related activities and formats them into readable messages for Discord.

🔍 Features
The SIEM tool focuses on detecting and alerting the following events:

* User Account Creation: Identifies when new user accounts are added.
* Password Change Attempts: Monitors both successful and failed password change endeavors.
* Successful and Failed Logons: Tracks user logon activities to detect unauthorized access attempts.
* Password Resets: Alerts when passwords are reset, which could indicate potential security concerns.
* Application Installations: Detects when new applications are installed, helping to prevent unauthorized software deployment.
* USB Device Insertions: Monitors the insertion of USB devices, a common vector for data exfiltration or malware introduction.

🔧 Events Monitored

The tool listens to these Windows Event IDs:


| Event ID | Description           |
| -------- | --------------------- |
| 4624     | Successful Logon      |
| 4625     | Failed Logon          |
| 4720     | User Account Created  |
| 4723     | Password Change       |
| 4724     | Password Reset        |
| 11707    | Application Installed |
| 6416     | USB Device Inserted   |

Each of these is tagged with an emoji in the Discord notification to improve readability.

🔔 Real-Time Notifications with Discord

The tool sends alerts using Discord webhooks. Each alert includes:

* Event type and ID
* Time of occurrence
* Source of the event

Extracted details (e.g., account name, application, USB device)

🚀 Getting Started
To deploy the SIEM tool:

1. Set Up Discord Webhook: Create a webhook in your desired Discord channel to receive alerts.

2. Configure the Tool: Input the webhook URL into the tool's configuration.

3. Run the Script: Execute the Python script with Administrative Privileges on the Windows machine.

4. Monitor Alerts: Security events will now be sent to your Discord channel in real-time.

🛠️ Setting Up Windows Logging via Group Policy

To make sure these events are logged by Windows, configure Advanced Audit Policy Settings via Group Policy:

Open `gpedit.msc`

Navigate to:

Computer Configuration → Windows Settings → Security Settings → Advanced Audit Policy Configuration

Enable the following:

* Logon/Logoff > Audit Logon Events (Success/Failure)
* Account Management > Audit User Account Management (Success)
* Object Access > Audit Removable Storage (Success)
* System > Audit System Events
* Privilege Use > Audit Sensitive Privilege Use

Apply and update policies with `gpupdate /force`.
