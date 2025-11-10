import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.email_smtp_host
        self.smtp_port = settings.email_smtp_port
        self.smtp_user = settings.email_smtp_user
        self.smtp_password = settings.email_smtp_password
        self.from_address = settings.email_from_address
        self.from_name = settings.email_from_name

    async def send_verification_code(
        self,
        to_email: str,
        code: str
    ) -> bool:
        subject = '[BootRun] 이메일 인증 코드'
        html_content = f'''
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2e6ff2;">BootRun 이메일 인증</h2>
                    <p>안녕하세요,</p>
                    <p>BootRun 회원가입을 위한 인증 코드입니다:</p>
                    <div style="background-color: #f5f5f5; padding: 20px;
                                text-align: center; margin: 20px 0;
                                border-radius: 5px;">
                        <h1 style="color: #2e6ff2; margin: 0;
                                   letter-spacing: 5px;">
                            {code}
                        </h1>
                    </div>
                    <p>이 코드는 30분간 유효합니다.</p>
                    <p>본인이 요청하지 않았다면 이 메일을 무시하세요.</p>
                    <hr style="border: none; border-top: 1px solid #ddd;
                               margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        BootRun - ICT 교육 플랫폼
                    </p>
                </div>
            </body>
        </html>
        '''
        return await self.send_email(to_email, subject, html_content)

    async def send_password_reset(
        self,
        to_email: str,
        reset_link: str
    ) -> bool:
        subject = '[BootRun] 비밀번호 재설정 요청'
        html_content = f'''
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2e6ff2;">비밀번호 재설정</h2>
                    <p>안녕하세요,</p>
                    <p>BootRun 계정의 비밀번호 재설정 요청을 받았습니다.</p>
                    <p>아래 버튼을 클릭하여 비밀번호를 재설정하세요:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}"
                           style="background-color: #2e6ff2; color: white;
                                  padding: 12px 30px; text-decoration: none;
                                  border-radius: 5px; display: inline-block;">
                            비밀번호 재설정
                        </a>
                    </div>
                    <p>또는 다음 링크를 복사하여 브라우저에 붙여넣으세요:</p>
                    <p style="word-break: break-all; color: #666;">
                        {reset_link}
                    </p>
                    <p>이 링크는 30분간 유효합니다.</p>
                    <p>본인이 요청하지 않았다면 이 메일을 무시하세요.</p>
                    <hr style="border: none; border-top: 1px solid #ddd;
                               margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        BootRun - ICT 교육 플랫폼
                    </p>
                </div>
            </body>
        </html>
        '''
        return await self.send_email(to_email, subject, html_content)

    async def send_welcome_email(
        self,
        to_email: str,
        nickname: str
    ) -> bool:
        subject = '[BootRun] 회원가입을 환영합니다!'
        html_content = f'''
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2e6ff2;">
                        환영합니다, {nickname}님!
                    </h2>
                    <p>BootRun에 가입해 주셔서 감사합니다.</p>
                    <p>이제 다양한 ICT 교육 콘텐츠를 학습하실 수 있습니다.</p>
                    <ul>
                        <li>전문가가 만든 고품질 강의</li>
                        <li>실습 중심의 프로젝트</li>
                        <li>수료증 발급</li>
                        <li>커뮤니티를 통한 네트워킹</li>
                    </ul>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://bootrun.com/courses"
                           style="background-color: #2e6ff2; color: white;
                                  padding: 12px 30px; text-decoration: none;
                                  border-radius: 5px; display: inline-block;">
                            강의 둘러보기
                        </a>
                    </div>
                    <hr style="border: none; border-top: 1px solid #ddd;
                               margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        BootRun - ICT 교육 플랫폼
                    </p>
                </div>
            </body>
        </html>
        '''
        return await self.send_email(to_email, subject, html_content)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.from_name} <{self.from_address}>'
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                recipients = [to_email] + (cc if cc else [])
                server.sendmail(
                    self.from_address,
                    recipients,
                    msg.as_string()
                )

            logger.info(f'이메일 전송 성공: {to_email}')
            return True

        except Exception as e:
            logger.error(f'이메일 전송 실패: {to_email}, 오류: {e}')
            return False


email_service = EmailService()
