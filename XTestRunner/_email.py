import os
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from XTestRunner.config import Config
from jinja2 import Environment, FileSystemLoader

from XTestRunner.config import RunResult

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(BASE_DIR, "html")
INIT_FILE = os.path.join(BASE_DIR, "__init__.py")
env = Environment(loader=FileSystemLoader(HTML_DIR))


class SMTP(object):
    """
    Mail function based on SMTP protocol
    """

    def __init__(self, user, password, host, port=None, ssl=True, tls=True, language=None):
        """
        SMTP send email.
        :param user: Email login username
        :param password: Email login password
        :param host: Email service address
        :param port: Email service post
        :param ssl: SMTP SSL True/False
        :param tls: TLS mode True/False
        :param language:
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port) if port is not None else (465 if ssl else 587)
        self.ssl = ssl
        self.tls = tls
        self.language = language
        if language is None:
            self.language = Config.language

    def sender(self, to=None, subject=None, contents=None, attachments=None):
        if to is None:
            raise ValueError("Please specify the email address to send")

        if isinstance(to, str):
            to = [to]

        if isinstance(to, list) is False:
            raise ValueError("Received mail type error")

        if subject is None:
            subject = RunResult.title
        if contents is None:
            email_template = "mail-en.html"
            if self.language == "en":
                email_template = "mail-en.html"
            elif self.language == "zh-CN":
                email_template = "mail-zh-CN.html"
            contents = env.get_template(email_template).render(
                mail_title=str(RunResult.title),
                start_time=str(RunResult.start_time),
                end_time=str(RunResult.end_time),
                mail_tester=str(RunResult.tester),
                duration=str(RunResult.duration),
                mail_pass=str(RunResult.passed),
                pass_rate=str(RunResult.pass_rate),
                mail_fail=str(RunResult.failed),
                failure_rate=str(RunResult.failure_rate),
                mail_error=str(RunResult.errors),
                error_rate=str(RunResult.error_rate),
                mail_skip=str(RunResult.skipped),
                skip_rate=str(RunResult.skip_rate)
            )

        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.user
        msg['To'] = ",".join(to)

        text = MIMEText(contents, 'html', 'utf-8')
        msg.attach(text)

        if attachments is not None:
            att_name = "report.html"
            if "\\" in attachments:
                att_name = attachments.split("\\")[-1]
            if "/" in attachments:
                att_name = attachments.split("/")[-1]

            att = MIMEApplication(open(attachments, 'rb').read())
            att['Content-Type'] = 'application/octet-stream'
            att.add_header('Content-Disposition', 'attachment', filename=att_name)
            msg.attach(att)

        smtp = smtplib.SMTP_SSL(self.host, self.port) if self.ssl else smtplib.SMTP(self.host, self.port)
        if self.tls is True and self.ssl is False:
            smtp.starttls()
        try:
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, to, msg.as_string())
            print(" 📧 Email sent successfully!!")
        except BaseException as msg:
            print('❌ Email failed to send!!' + msg.__str__())
        finally:
            smtp.quit()
