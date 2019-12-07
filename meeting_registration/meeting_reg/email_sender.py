# -*- coding: utf-8 -*-
"""
Module that sends email

Example:

    sender = EmailSender("smtp.gmail.com", "youremail@gmail.com", "your_email_password")
    my_letter = '''
        Subject: This letter about smth

        Hello, World!
    '''
    sender.send_mail_to_person("reciever@gmail.com", my_letter)
    receivers = ["reciever1@gmail.com", "reciever2@gmail.com", "reciever3@gmail.com"]
    sender.send_mail_to_people(receivers, my_letter)

Todo:
    * Email constructor
    * Emails sent limitations like queue

"""
import smtplib
import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List


@dataclass
class Config:
    smtp_server_address: str
    sender_email: str
    password: str
    port: int = 465
    context: ssl.SSLContext = ssl.create_default_context()


class EmailSender:
    cfg: Config

    def __init__(self, smtp_server_address: str, sender_email: str, password: str):
        self.cfg = Config(smtp_server_address, sender_email, password)

    def send_mail_to_person(self, receiver_email: str, message: MIMEMultipart):
        """
        Function that sends email to single person
        Args:
            server (smtplib.SMTP_SSL): access to sender sever
            receiver_email (str): email address of receiver ("reciever@gmail.com")
            message (str): text that will be sent

        Returns:

        """
        with smtplib.SMTP_SSL(self.cfg.smtp_server_address, self.cfg.port, context=self.cfg.context) as server:
            server.login(self.cfg.sender_email, self.cfg.password)
            server.sendmail(self.cfg.sender_email, receiver_email, message.as_string())

    def send_mails_to_people(self, receiver_emails: List[str], message: MIMEMultipart):
        """
        Function that sends emails with same content to multiple people
        Args:
            receiver_emails: list of email address (["reciever1@gmail.com", "receiver2@ya.ru"])
            message: text that will be sent

        Returns:

        """
        for email in receiver_emails:
            self.send_mail_to_person(email, message)

    @staticmethod
    def construct_message(text, encoding="utf-8"):
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(text, "plain", encoding))
        return message

    def send_alert_to_teacher(self, teacher, parents):
        header = f"""Добрый день, {teacher["name"]}.\nНа встречу с вами записалось {len(parents)} родителей:"""
        lister = " ".join(f"{parent['parent_name']} - {parent['student_name']} ({parent['student_grade']})"
                          for parent in parents)
        self.send_mail_to_person(teacher["email"], self.construct_message(header + lister))
        print("mail_sent")
