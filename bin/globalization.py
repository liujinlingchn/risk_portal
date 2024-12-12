from conf import lang_zh_conf as lz
from conf import lang_en_conf as le
import logging

log = logging.getLogger()


class LangPackages(object):

    def __init__(self, langs):
        self.langpackages = self._import_lang_packages(langs)

    def _patch(self, conf_lang, data_lang):

        def type_dict(lang_value, k, v):
            # 没有这个属性 加上
            if lang_value is None:
                setattr(data_lang, k, v)

            # 如果类型不一样，报错
            elif not isinstance(lang_value, dict):
                raise TypeError('配置文件类型不合法')

            # 有这个字典属性，更新
            elif lang_value is not None and isinstance(lang_value, dict):
                lang_value.update(v)

        def type_list(lang_value, k, v):
            # 没有这个属性 加上
            if lang_value is None:
                setattr(data_lang, k, v)

            # 如果类型不一样，报错
            elif not isinstance(lang_value, list):
                raise TypeError('配置文件类型不合法')

            # 有这个列表属性，更新
            elif lang_value is not None and isinstance(lang_value, list):
                lang_value = v
            return lang_value

        for k, v in conf_lang.__dict__.items():
            if k.startswith('__'):
                continue
            lang_value = getattr(data_lang, k, None)
            if isinstance(v, dict):
                type_dict(lang_value, k, v)

            if isinstance(v, list):
                lang_value_ = type_list(lang_value, k, v)
                if lang_value_:
                    setattr(data_lang, k, lang_value_)

            if isinstance(v, str):
                # 没有这个属性 加上
                if lang_value is None:
                    setattr(data_lang, k, v)

                # 如果类型不一样，报错
                elif not isinstance(lang_value, str):
                    raise TypeError('配置文件类型不合法')
                # 有这个属性，更新
                elif lang_value is not None and isinstance(lang_value, str):
                    setattr(data_lang, k, v)

            if isinstance(v, tuple):
                # 没有这个属性 加上
                if lang_value is None:
                    setattr(data_lang, k, v)

                # 如果类型不一样，报错
                elif not isinstance(lang_value, tuple):
                    raise TypeError('配置文件类型不合法')
                # 有这个属性，更新
                elif lang_value is not None and isinstance(lang_value, tuple):
                    setattr(data_lang, k, v)

            if isinstance(v, type):
                # 没有这个属性 加上
                if lang_value is None:
                    setattr(data_lang, k, v)

                # 如果类型不一样，报错
                elif not isinstance(lang_value, type):
                    raise TypeError('配置文件类型不合法')

                # 有这个属性，更新
                else:
                    for d, f in v.__dict__.items():
                        if d.startswith('__'):
                            continue
                        if isinstance(f, dict):
                            lang_value_ = getattr(lang_value, d, None)
                            type_dict(lang_value_, d, f)
                        elif isinstance(f, list):
                            lang_value_ = getattr(lang_value, d, None)
                            lang_value_ = type_list(lang_value_, d, f)
                            if lang_value_:
                                setattr(lang_value, d, lang_value_)
                        else:
                            setattr(lang_value, d, f)

    def _import_lang_packages(self, langs):
        return {'zh': lz, 'en': le}

    def __getitem__(self, lang):
        return self.langpackages[lang]


LANGS = LangPackages(['zh', 'en'])
