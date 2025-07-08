import pythoncom
import win32com.client as win32
import re

class EmailSender:
    @staticmethod
    def send_email(candidate_name, candidate_email):
        google_form_link = "https://calendly.com/automated-interview-scheduling/interviews-automation"
        calendly_link = f"{google_form_link}?name={candidate_name}&email={candidate_email}"

        pythoncom.CoInitialize()
        try:
            outlook = win32.Dispatch('Outlook.Application')
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            mail.To = candidate_email
            mail.Subject = f'Interview Scheduling Form - {candidate_name}'
            mail.Body = f"""
    Hello {candidate_name},

    Congratulations! Based on our evaluation, you are selected for the next round.

    Please use the following link to select your preferred time slot for the interview:

    {calendly_link}

    The interview will be conducted in person at our office. Kindly ensure you are available at the selected time and location.

    We look forward to meeting you!

    Regards,  
    HR Team
    """

            mail.Send()
            print("Email sent successfully!")

        except Exception as e:
            print("Error sending email:", e)


    @staticmethod
    def extract_email_from_text(text: str) -> str:
        """Extract email address from a given text."""
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return email_match.group(0) if email_match else None