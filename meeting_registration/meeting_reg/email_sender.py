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
    * Emails sent limitations like queue

"""
import smtplib
import ssl
import time
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from .tools import parse_date, beautiful_date


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

    def send_mails_to_people(self, receiver_emails: List[str], message: MIMEMultipart, delay=5):
        """
        Function that sends emails with same content to multiple people
        Args:
            receiver_emails: list of email address (["reciever1@gmail.com", "receiver2@ya.ru"])
            message: text that will be sent

        Returns:

        """
        for email in receiver_emails:
            time.sleep(delay)
            self.send_mail_to_person(email, message)

    @staticmethod
    def construct_message(text, header=None, encoding="utf-8"):
        message = MIMEMultipart("alternative")
        msg_text = MIMEText(text, "plain", encoding)
        message["Subject"] = header
        message.attach(msg_text)
        return message

    def send_alert_to_teacher(self, teacher, parents):
        header = f'К вами записалось {len(parents)} родителей.\n'
        top = f'Добрый день, {teacher["name"]}.\nНа встречу с вами записалось {len(parents)} родителей:\n\n'
        lister = "\n".join(f"{parent['parent_name']} ({parent['student_name']}, {parent['student_grade']})"
                           for parent in parents)
        self.send_mail_to_person(teacher["email"], self.construct_message(top + lister, header=header))

    def send_alert_to_parent(self, parent, teachers, day, cancel_url, re_reg_url):
        date = beautiful_date(*parse_date(day.date()))
        time = day.time()
        header = f'Регистрация на день открытых дверей {date}'
        top = f"Добрый день, {parent.parent_name}.\n" \
              f"{date} в {time} в школе 1543 пройдет день открытых дверей.\n" \
              f"Вы зарегистрировались для посещения следующих учителей {parent.student_grade} класса:\n\n"
        lister = "\n".join(f"{teacher.name} ({teacher.subject})" for teacher in teachers)
        footer = f"\n\nЕсли вы хотите отвемить заявку, то, пожалуйста, перейдите по этой ссылке:\n{cancel_url}\n\n" \
                 f"Если вы хотите изменить список учителей в заявке, то перейдите по этой ссылке:\n{re_reg_url}\n\n" \
                 f"Искренне Ваша, Администрация 1543"
        self.send_mail_to_person(parent.parent_email, self.construct_message(top + lister + footer, header=header))

    def send_cancel_application(self, parent, url):
        header = f"Ваша заявка на день открытых дней была удалена."
        top = f"Добрый день, {parent.parent_name}." \
              f"Ваша заявка на день открытых дней была удалена.\n" \
              f"Для повторной регистрации перейдите по ссылке:\n{url}" \
              f"Искренне Ваша, Администрация 1543."
        self.send_mail_to_person(parent.parent_email, self.construct_message(top, header=header))
