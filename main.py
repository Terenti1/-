import re
import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window


class CalcRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10),
                         spacing=dp(8), **kwargs)

        # --- Место для картинки ---
        img_box = BoxLayout(size_hint_y=None, height=dp(180))
        self.image = Image(source='images.jpg',
                           allow_stretch=True, keep_ratio=True)
        img_box.add_widget(self.image)
        self.add_widget(img_box)

        # --- Дисплей ---
        self.display = Label(
            text='0', font_size=dp(40),
            halign='right', valign='middle',
            size_hint_y=None, height=dp(90),
            color=(1, 1, 1, 1),
        )
        self.display.bind(size=lambda s, v: setattr(s, 'text_size', v))
        self.add_widget(self.display)

        # --- Кнопки ---
        grid = GridLayout(cols=4, spacing=dp(6))
        layout = [
            ('C', 'clear'), ('√', 'sqrt'), ('^', 'op'),       ('÷', 'op'),
            ('7', 'num'),   ('8', 'num'),  ('9', 'num'),      ('×', 'op'),
            ('4', 'num'),   ('5', 'num'),  ('6', 'num'),      ('-', 'op'),
            ('1', 'num'),   ('2', 'num'),  ('3', 'num'),      ('+', 'op'),
            ('0', 'num'),   ('.', 'num'),  ('<[x]', 'back'),  ('=', 'eq'),
        ]
        for text, kind in layout:
            btn = Button(text=text, font_size=dp(26),
                         background_normal='',
                         background_color=self._color(kind),
                         markup=False)
            # Сохраняем тип кнопки прямо в виджете.
            # Логика работает по типу, а не по тексту — не сломается,
            # если поменять надпись на кнопке.
            btn.kind = kind
            btn.bind(on_press=self.on_press)
            grid.add_widget(btn)
        self.add_widget(grid)

        self.expression = ''

    @staticmethod
    def _color(kind):
        if kind == 'op':
            return (0.20, 0.45, 0.75, 1)   # синие — операции
        if kind == 'eq':
            return (0.20, 0.65, 0.35, 1)   # зелёная — равно
        if kind in ('clear', 'back'):
            return (0.75, 0.30, 0.30, 1)   # красные — очистка
        return (0.25, 0.25, 0.28, 1)       # серые — цифры

    def on_press(self, instance):
        # Логика идёт ПО ТИПУ КНОПКИ, а не по её надписи.
        kind = getattr(instance, 'kind', None)
        t = instance.text

        if kind == 'clear':
            self.expression = ''
            self.display.text = '0'
            return

        if kind == 'back':
            self.expression = self.expression[:-1]
            self.display.text = self.expression or '0'
            return

        if kind == 'sqrt':
            self._apply_sqrt()
            return

        if kind == 'eq':
            try:
                res = self._eval(self.expression or '0')
                self.expression = self._fmt(res)
                self.display.text = self.expression
            except Exception:
                self.display.text = 'Ошибка'
                self.expression = ''
            return

        # Осталось: цифры, точка, операции.
        ch = t
        if ch == '×':
            ch = '*'
        elif ch == '÷':
            ch = '/'
        self.expression += ch
        self.display.text = self.expression

    def _apply_sqrt(self):
        """Извлекает корень из последнего числа в выражении."""
        m = re.search(r'(\d+\.?\d*)$', self.expression)
        if not m:
            self.expression = self._fmt(math.sqrt(0))
            self.display.text = self.expression
            return
        try:
            num = float(m.group(1))
            if num < 0:
                raise ValueError
            res = math.sqrt(num)
            self.expression = self.expression[:m.start()] + self._fmt(res)
            self.display.text = self.expression
        except Exception:
            self.display.text = 'Ошибка'
            self.expression = ''

    @staticmethod
    def _eval(expr):
        """Безопасное вычисление выражения."""
        allowed = set('0123456789.+-*/()^ ')
        if not set(expr).issubset(allowed):
            raise ValueError('invalid characters')
        expr = expr.replace('^', '**')
        return eval(expr, {'__builtins__': {}}, {})

    @staticmethod
    def _fmt(val):
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val))
            return ('%.10f' % val).rstrip('0').rstrip('.')
        return str(val)


class CalcApp(App):
    def build(self):
        Window.clearcolor = (0.10, 0.10, 0.12, 1)   # тёмный фон
        return CalcRoot()


if __name__ == '__main__':
    CalcApp().run()
