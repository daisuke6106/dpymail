from abc import ABC
import email
from email.header import decode_header
from email.utils import getaddresses

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
        self.mailserveronnection = mailserveronnection


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
        self.uid = uid
        self.msg_data = msg_data

        # メールオブジェクトに変換
        msg = email.message_from_bytes(msg_data[0][1])

        # 送信元メールアドレス取得
        from_header = self.__decode_mime_header(msg.get("From"))
        from_address = self.__get_addresses(from_header)

        # 送信先メールアドレス取得
        to_header = self.__decode_mime_header(msg.get("To"))
        to_address = self.__get_addresses(to_header)

        # 件名取得
        subject = self.__decode_mime_header(msg["Subject"])

        # 本文取得
        body = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                # 添付ファイルでないテキスト部分を探す
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore")
                    break
        else:
            # シングルパートメール
            body = msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="ignore")

        if body:
            print(f"送信元: {from_address}")
            print(f"送信先: {to_address}")
            print(f"件名: {subject}")
            print(f"本文（先頭100文字）:\n{body[:100]}...")
        else:
            print(f"送信元: {from_address}")
            print(f"送信先: {to_address}")
            print(f"件名: {subject}")
            print("本文が見つかりません")

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
