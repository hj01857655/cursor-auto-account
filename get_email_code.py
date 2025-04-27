import logging
import re
import time
import requests


class EmailVerificationHandler:
    def __init__(self,account):
        self.username = 'zoowayss'
        self.session = requests.Session()
        self.account = account
        self.emailExtension = '@mailto.plus'

    def get_verification_code(self, max_retries=5, retry_interval=60):
        """
        获取验证码，带有重试机制。

        Args:
            max_retries: 最大重试次数。
            retry_interval: 重试间隔时间（秒）。

        Returns:
            验证码 (字符串或 None)。
        """

        for attempt in range(max_retries):
            try:
                logging.info(f"尝试获取验证码 (第 {attempt + 1}/{max_retries} 次)...")
                verify_code, first_id = self._get_latest_mail_code()
                if verify_code is not None and first_id is not None:
                    self._cleanup_mail(first_id)
                return verify_code
            except Exception as e:
                logging.error(f"获取验证码失败: {e}")  # 记录更一般的异常
                if attempt < max_retries - 1:
                    logging.error(f"发生错误，{retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    raise Exception(f"获取验证码失败且已达最大重试次数: {e}") from e

        raise Exception(f"经过 {max_retries} 次尝试后仍未获取到验证码。")


    # 手动输入验证码
    def _get_latest_mail_code(self):
        # 获取邮件列表
        mail_list_url = f"https://tempmail.plus/api/mails?email={self.username}{self.emailExtension}&limit=20&epin={self.account}"
        mail_list_response = self.session.get(mail_list_url)
        mail_list_data = mail_list_response.json()
        print(mail_list_data)
        time.sleep(0.5)
        if not mail_list_data.get("result"):
            return None, None

        # 获取最新邮件的ID
        first_id = mail_list_data.get("first_id")
        if not first_id:
            return None, None

        # 获取具体邮件内容
        mail_detail_url = f"https://tempmail.plus/api/mails/{first_id}?email={self.username}{self.emailExtension}&epin={self.account}"
        mail_detail_response = self.session.get(mail_detail_url)
        mail_detail_data = mail_detail_response.json()
        time.sleep(0.5)
        if not mail_detail_data.get("result"):
            return None, None

        # 从邮件文本中提取6位数字验证码
        mail_text = mail_detail_data.get("text", "")
        mail_subject = mail_detail_data.get("subject", "")
        logging.info(f"找到邮件主题: {mail_subject}")
        # 修改正则表达式，确保 6 位数字不紧跟在字母或域名相关符号后面
        code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", mail_text)

        if code_match:
            return code_match.group(), first_id
        return None, None

        
    def _cleanup_mail(self, first_id):
        # 构造删除请求的URL和数据
        delete_url = "https://tempmail.plus/api/mails/"
        payload = {
            "email": f"{self.username}{self.emailExtension}",
            "first_id": first_id,
            "epin": f"{self.account}",
        }

        # 最多尝试5次
        for _ in range(5):
            response = self.session.delete(delete_url, data=payload)
            try:
                result = response.json().get("result")
                if result is True:
                    return True
            except:
                pass

            # 如果失败,等待0.5秒后重试
            time.sleep(0.5)

        return False


if __name__ == "__main__":
    email_handler = EmailVerificationHandler('yuaotian@zoowayss.top')
    code = email_handler.get_verification_code()
    print(code)
