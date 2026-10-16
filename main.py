import re
import math
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock


# 🔑 СЕКРЕТНЫЙ КОД. Введите его и нажмите "=" — сработает взрыв.
NUCLEAR_CODE = "7319"

# Длительность показа взрыва в секундах
BOOM_DURATION = 4.0


class CalcRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ================= СЛОЙ 1: калькулятор =================
        root = BoxLayout(orientation='vertical', padding=dp(10),
                         spacing=dp(8), size_hint=(1, 1))
        self.add_widget(root)

        # --- Картинка шапки ---
        img_box = BoxLayout()
        self.image = Image(source='images.jpg',
                           allow_stretch=True, keep_ratio=True)
        img_box.add_widget(self.image)
        root.add_widget(img_box)

        # --- Дисплей ---
        self.display = Label(
            text='0', font_size=dp(40),
            halign='right', valign='middle',
            size_hint_y=None, height=dp(80),
            color=(1, 1, 1, 1),
        )
        self.display.bind(size=lambda s, v: setattr(s, 'text_size', v))
        root.add_widget(self.display)

        # --- Кнопки ---
        self.grid = GridLayout(cols=4, spacing=dp(6), size_hint_y=None)
        self.grid.bind(width=self._sync_grid_height)

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
            btn.kind = kind
            btn.bind(on_press=self.on_press)
            self.grid.add_widget(btn)
        root.add_widget(self.grid)

        self.expression = ''

        # ================= СЛОЙ 2: взрыв поверх всего =================
        self.explosion = Image(
            source='nuclear-bomb-explosion-u71b251wgftmlgpb.gif',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
            opacity=0,
            anim_delay=0.06,
        )
        self.add_widget(self.explosion)

        # Оранжевая вспышка
        with self.canvas.after:
            self._flash_color = Color(1, 0.55, 0.1, 0)
            self._flash_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_flash, size=self._sync_flash)

    # ------- геометрия -------

    def _sync_flash(self, *args):
        self._flash_rect.pos = self.pos
        self._flash_rect.size = self.size

    def _sync_grid_height(self, grid, width):
        cell = (width - dp(6) * 3) / 4
        grid.height = cell * 5 + dp(6) * 4

    # ------- цвета -------

    @staticmethod
    def _color(kind):
        if kind in ('op', 'sqrt'):
            return (0.20, 0.45, 0.75, 1)
        if kind == 'eq':
            return (0.20, 0.65, 0.35, 1)
        if kind in ('clear', 'back'):
            return (0.75, 0.30, 0.30, 1)
        return (0.25, 0.25, 0.28, 1)

    # ------- логика кнопок -------

    def on_press(self, instance):
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
            # 🎇 Проверка секретного кода
            if self.expression == NUCLEAR_CODE:
                self.expression = ''
                self.display.text = '☢'
                self._nuclear_boom()
                return
            # Обычное вычисление
            try:
                res = self._eval(self.expression or '0')
                self.expression = self._fmt(res)
                self.display.text = self.expression
                self._little_pulse()
            except Exception:
                self.display.text = 'Ошибка'
                self.expression = ''
            return

        ch = t
        if ch == '×':
            ch = '*'
        elif ch == '÷':
            ch = '/'
        self.expression += ch
        self.display.text = self.expression

    # ------- корень -------

    def _apply_sqrt(self):
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

    # ------- анимации -------

    def _little_pulse(self):
        (Animation(font_size=dp(54), duration=0.08) +
         Animation(font_size=dp(40), duration=0.25,
                   transition='out_back')).start(self.display)

    def _nuclear_boom(self):
        try:
            self.explosion.anim_reset(True)
        except Exception:
            pass
        self.explosion.opacity = 1

        self._flash_color.rgba = (1, 0.75, 0.2, 0)
        (Animation(rgba=(1, 0.85, 0.3, 0.9), duration=0.12) +
         Animation(rgba=(1, 0.55, 0.1, 0.0), duration=0.9,
                   transition='out_quad')).start(self._flash_color)

        (Animation(x=self.display.x + dp(6), duration=0.05) +
         Animation(x=self.display.x - dp(6), duration=0.05) +
         Animation(x=self.display.x,        duration=0.05)).start(self.display)

        Clock.schedule_once(self._hide_boom, BOOM_DURATION)

    def _hide_boom(self, *args):
        Animation(opacity=0, duration=0.4).start(self.explosion)
        self.display.text = '0'

    # ------- вычисление -------

    @staticmethod
    def _eval(expr):
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
        Window.clearcolor = (0.10, 0.10, 0.12, 1)
        return CalcRoot()


if __name__ == '__main__':
    CalcApp().run()
