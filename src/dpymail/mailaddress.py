class MailAddress:
    """メールアドレスを表すクラス
    """

    def __init__(self, mailaddress: str, name: str):
        """コンストラクタ

        メールアドレスとその名称（設定されている場合）を元にメールアドレスを表すインスタンスを生成する

        Args:
            mailaddress (str): メールアドレス
            name (str): 名称
        """
        self._mailaddress = mailaddress

        if name:
            self._has_name = True
            self._name = name
        else:
            self._has_name = False
            self._name = ""

        # メールアドレスをユーザ部、ドメイン部で分割して保持
        user, domain = mailaddress.split("@", 1)
        self._mailaddress_user_area = user
        self._mailaddress_dmail_area = domain

        # ユーザ部にプラスアドレスであるか確認する
        if "+" in user:
            self._is_plusaddress = True
            base_user, tag = user.split("+", 1)
            self._mailaddress_user_plus_bsae_user_area = base_user
            self._mailaddress_user_plus_tag_area = tag
        else:
            self._is_plusaddress = False
            self._mailaddress_user_plus_bsae_user_area = user
            self._mailaddress_user_plus_tag_area = ""

    def get_mailaddress(self) -> str:
        """メールアドレスを取得する

        Returns:
            str: メールアドレス
        """
        return self._mailaddress

    def has_name(self) -> bool:
        """名称があるかの判定結果を返却する

        Returns:
            bool: True：有り、False：無し
        """
        return self._has_name

    def get_name(self) -> str:
        """名称を取得する

        名称がないメールアドレスの場合、空文字を返却する

        Returns:
            str: 名称
        """
        return self._name

    def get_mailaddress_user_area(self) -> str:
        """メールアドレスのユーザ部を取得する

        Returns:
            str: メールアドレスのユーザ部
        """
        return self._mailaddress_user_area

    def is_plusaddress(self) -> bool:
        """メールアドレスがプラスアドレスかの判定結果を返却する

        Returns:
            bool: True：有り、False：無し
        """
        return self._is_plusaddress

    def get_plusaddresss_basename(self) -> str:
        """プラスアドレスのベース名（+の前半部）を返却する

        これがプラスアドレスではない場合、ユーザ部と同じ結果を返却する

        Returns:
            str: プラスアドレスのベース名
        """
        return self._mailaddress_user_plus_bsae_user_area

    def get_plusaddress_tagname(self) -> str:
        """プラスアドレスのタグ名（+の後半部）を返却する

        これがプラスアドレスではない場合、空文字を返却する

        Returns:
            str: プラスアドレスのタグ名
        """
        return self._mailaddress_user_plus_tag_area

    def get_mailaddress_dmain_area(self) -> str:
        """メールアドレスのドメイン部を取得する

        Returns:
            str: メールアドレスのドメイン部
        """
        return self._mailaddress_dmail_area

    def __str__(self):
        if self.has_name():
            return f"{self.get_name()} <{self.get_mailaddress()}>"
        else:
            return f"{self.get_mailaddress()}"
