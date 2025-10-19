from abc import ABC
import email
from email.header import decode_header
from email.utils import getaddresses
from html.parser import HTMLParser

from mailaddress import MailAddress


class Mail(ABC):
    """メールを表す抽象クラス
    """

    def __init__(self, mailserveronnection):
        """コンストラクタ

        メールサーバコネクションを元にメールインスタンスを生成する

        Args:
            mailserveronnection (MailServerConnection): メールサーバコネクション
        """
        self._mailserveronnection = mailserveronnection


class IMAPMail(Mail):
    """IMAPメールを表すメールクラス
    """

    def __init__(self, uid: bytes, msg_data, mailserveronnection):
        """コンストラクタ

        メールサーバコネクションを元にメールインスタンスを生成する

        Args:
            uid (bytes): メールUID
            msg_data : メール情報
            mailserveronnection (MailServerConnection): メールサーバコネクション
        """
        super().__init__(mailserveronnection)
        self._uid = uid
        self._msg_data = msg_data

        # メールオブジェクトに変換
        msg = email.message_from_bytes(msg_data[0][1])

        # 送信元メールアドレス取得
        self._from_address = self.__get_addresses(
            self.__decode_mime_header(msg.get("From")))

        # 送信先メールアドレス取得
        self._to_address = self.__get_addresses(
            self.__decode_mime_header(msg.get("To")))

        # 件名取得
        self._subject = self.__decode_mime_header(msg["Subject"])

        # 本文取得
        self._body_org = None

        # マルチパートメールの場合
        if msg.is_multipart():
            self._is_multipart = True
            for part in msg.walk():
                self._content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                # 添付ファイルでないテキスト部分を探す
                if self._content_type == "text/plain" and "attachment" not in content_disposition:
                    self._body_org = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore")
                    break

        # シングルパートメールの場合
        else:
            self._is_multipart = False
            self._content_type = msg.get_content_type()
            self._body_org = msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="ignore")

        # 本文オブジェクト作成
        if self._body_org:
            if self._content_type == "text/html":
                self._mail_body = HTMLMailBody(
                    self._content_type, self._body_org)
            else:
                self._mail_body = PlainTextMailBody(
                    self._content_type, self._body_org)
        else:
            self._mail_body = PlainTextMailBody("text/plain", "")

        # if self._body_org:
        #     print(f"送信元: {self._from_address[0]}")
        #     print(f"送信先: {self._to_address[0]}")
        #     print(f"件名: {self._subject}")
        #     print(f"本文（先頭100文字）:\n{self.get_mail_body()}...")
        #     print(f"content-type:{self._content_type}")
        #     print(f"isultipart:{self._is_multipart}")
        # else:
        #     print(f"送信元: {self._from_address[0]}")
        #     print(f"送信先: {self._to_address[0]}")
        #     print(f"件名: {self._subject}")
        #     print("本文が見つかりません")

    def from_address(self) -> MailAddress:
        """送信元メールアドレスを取得する

        Returns:
            MailAddress: 送信元メールアドレス
        """
        return self._from_address[0] if self._from_address else None

    def to_address(self) -> list[MailAddress]:
        """送信先メールアドレスを取得する

        Returns:
            list[MailAddress]: 送信先メールアドレス一覧
        """
        return self._to_address

    def get_subject(self) -> str:
        """件名を取得する

        Returns:
            str: 件名
        """
        return self._subject

    def get_mail_body(self) -> "MailBody":
        """メール本文を取得する

        Returns:
            MailBody: メール本文インスタンス
        """
        return self._mail_body

    def __decode_mime_header(self, value) -> str:
        """MIMEヘッダーをデコードｊ

        Args:
            value (header): デコード対象MIMEヘッダ

        Returns:
            str: デコードした文字列
        """
        if value is None:
            return ""

        # MIMEエンコードを元に戻す。
        decoded_parts = decode_header(value)

        decoded_str = ""
        for part, enc in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(enc or "utf-8", errors="ignore")
            else:
                decoded_str += part
        return decoded_str

    def __get_addresses(self, header_value) -> list[MailAddress]:
        """メールアドレス取得

        ヘッダ情報からメールアドレスを抽出してメールアドレスインスタンスにして返却する。

        Args:
            header_value : ヘッダ値

        Returns:
            list[MailAddress]: メールアドレス一覧
        """
        if not header_value:
            return []
        # ヘッダ（From, To など）からメールアドレスを抽出
        # 複数宛先がある場合はリストで返す
        addresses = getaddresses([header_value])
        return [self._create_mailaddress_instance(addr, name) for name, addr in addresses if addr]

    def _create_mailaddress_instance(self, address: str, name: str) -> MailAddress:
        """メールアドレスインスタンスを作成して返却

        Args:
            address (str): メールアドレス文字列
            name (str): 名称

        Returns:
            MailAddress: メールアドレスインスタンス
        """
        return MailAddress(address, name)


class MailBody(ABC):
    """メール本文を表抽象クラス
    """

    def __init__(self, content_type: str, content: str):
        """コンストラクタ

        メール本文内容とそのコンテンツタイプを元にメール本文インスタンスを生成する

        Args:
            content_type (str): コンテンツタイプ
            content (str): メール本文内容
        """
        self._content_type = content_type
        self._content = content

    def __str__(self):
        return self._content


class PlainTextMailBody(MailBody):
    """プレーンテキストメール本文を表すクラス
    """

    def __init__(self, content_type: str, content: str):
        """コンストラクタ

        メール本文内容を元にプレーンテキストメール本文インスタンスを生成する

        Args:
            content_type (str): コンテンツタイプ
            content (str): メール本文内容
        """
        super().__init__(content_type, content)


class HTMLMailBody(MailBody):
    """HTMLメール本文を表すクラス
    """

    class _HtmlParser(HTMLParser):
        """HTMLパーサークラス
        """

        def __init__(self):
            super().__init__()
            self.text_parts = []

        def handle_data(self, data):
            # dataが改行のみの場合は無視する
            if data.strip():
                self.text_parts.append(data)

        def get_text(self) -> str:
            return ''.join(self.text_parts)

    def __init__(self, content_type: str, content: str):
        """コンストラクタ

        メール本文内容を元にHTMLメール本文インスタンスを生成する

        Args:
            content_type (str): コンテンツタイプ
            content (str): メール本文内容
        """
        super().__init__(content_type, content)

        # HTMLをパースし保持する
        self._html_content = self._HtmlParser()
        self._html_content.feed(content)

    def __str__(self):
        return self._html_content.get_text()
