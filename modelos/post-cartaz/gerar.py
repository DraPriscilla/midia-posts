"""post-cartaz: carrossel de 5 cards com foto da Dra. Priscilla segurando um cartaz.
Uso: python3 gerar.py specs.json <pcd|mulher|ear>
As fotos ficam em ./fotos e as fontes em ./fonts (mesma pasta deste arquivo)."""
import json, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
import os as _o
BASE = _o.path.dirname(_o.path.abspath(__file__))
FD = BASE + "/fonts/"
UP = BASE + "/fotos/"
GOLD = (226, 176, 40)
INK = (22, 18, 14)
CARD = (201, 164, 108)
CARD_DARK = (176, 138, 84)
TARJA = INK
TARJA_TXT = GOLD
NUM_TXT = GOLD
PILL = (26, 22, 16)
PILL_TXT = GOLD
HANDLE = "@leisparapcd"
CHAMADA = "Curso gratuito no link da bio"

def set_brand(b):
    global GOLD, INK, CARD, CARD_DARK, TARJA, TARJA_TXT, NUM_TXT, PILL, PILL_TXT, HANDLE
    if b == "mulher":
        INK = (17, 17, 17); CARD = (246, 196, 212); CARD_DARK = (232, 160, 186)
        TARJA = (232, 24, 90); TARJA_TXT = (255, 255, 255); NUM_TXT = (255, 107, 154)
        PILL = (17, 17, 17); PILL_TXT = (255, 107, 154); GOLD = (255, 107, 154)
        HANDLE = "@leisparamulher"
    if b == "ear":
        INK = (24, 16, 10); CARD = (243, 232, 200); CARD_DARK = (220, 203, 156)
        TARJA = (212, 160, 23); TARJA_TXT = (24, 16, 10); NUM_TXT = (212, 160, 23)
        PILL = (24, 16, 10); PILL_TXT = (212, 160, 23); GOLD = (212, 160, 23)
        HANDLE = "@estudodealtorendimento"

import os as _os
FONTE = _os.environ.get("FONTE", "")
FONTES = {"marker": "PermanentMarker-Regular.ttf", "fraunces": "fraunces-latin-700-normal.ttf"}
ESCALA = {"marker": 1.0, "fraunces": 0.95, "cormorant": 1.12, "dmserif": 1.0, "outfit": 0.95}

def marker(size):
    size = int(size * ESCALA.get(FONTE, 1.0))
    if FONTE == "outfit":
        return outfit(size, 800)
    return ImageFont.truetype(FD + FONTES[FONTE], size)

def outfit(size, wght=500):
    f = ImageFont.truetype(FD + "Outfit-wght.ttf", size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f

# Topo de cada foto (fração da altura) = ponto mais alto (cabeça ou dedo)
FOTOS = {
    "cima": ("cima.jpg", 0.19),
    "um": ("um.jpg", 0.26),
    "dois": ("dois.jpg", 0.075),
    "tres": ("tres.jpg", 0.22),
    "baixo": ("baixo.jpg", 0.20),
}


def fundo(foto_key, topo_alvo):
    nome, frac = FOTOS[foto_key]
    im = Image.open(UP + nome).convert("RGB")
    sc = W / im.width
    im = im.resize((W, round(im.height * sc)), Image.LANCZOS)
    off = int(topo_alvo - frac * im.height)
    canvas = Image.new("RGB", (W, H))
    # preenche acima da foto com a cor da parede (linha do topo, desfocada)
    topo = im.crop((0, 0, W, 40)).resize((W, 1)).resize((W, max(off, 1)))
    topo = topo.filter(ImageFilter.GaussianBlur(30))
    if off > 0:
        canvas.paste(topo, (0, 0))
        # transição suave
        canvas.paste(im, (0, off))
        mask = Image.linear_gradient("L").resize((W, 120))
        faixa = im.crop((0, 0, W, 120))
        base = canvas.crop((0, off, W, off + 120))
        base_topo = topo.resize((W, 120)) if off > 0 else base
        canvas.paste(Image.composite(faixa, base_topo, mask), (0, off))
    else:
        canvas.paste(im, (0, off))
    # escurece o alto (como no post anterior) e a base
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(H):
        a = 0
        if y < 700:
            a = int(110 * (1 - y / 700) ** 1.4)
        if y > 1150:
            a = max(a, int(120 * ((y - 1150) / 200) ** 1.5))
        d.line([(0, y), (W, y)], fill=(28, 26, 44, a))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), ov)
    return canvas


def papelao(w, h):
    rnd = random.Random(w * 7 + h)
    im = Image.new("RGB", (w, h), CARD)
    d = ImageDraw.Draw(im)
    for x in range(0, w, 5):
        v = rnd.randint(-9, 6)
        c = tuple(max(0, min(255, k + v)) for k in CARD)
        d.line([(x, 0), (x, h)], fill=c, width=2)
    # leve variação vertical
    g = Image.linear_gradient("L").resize((w, h))
    escuro = Image.new("RGB", (w, h), CARD_DARK)
    im = Image.composite(escuro, im, g.point(lambda p: int(p * 0.35)))
    return im


def quebra(texto, fonte, largura, draw):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if draw.textlength(t, font=fonte) <= largura:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def placa(spec, w=960):
    """spec: {numero, linhas:[{t, destaque, sublinha}], corpo, tam}"""
    pad_top = 60
    tmp = Image.new("RGB", (10, 10))
    dd = ImageDraw.Draw(tmp)
    tam = spec.get("tam", 74)
    fm = marker(tam)
    elementos = []
    y = pad_top
    if spec.get("numero"):
        elementos.append(("num", y))
        y += 98
    for ln in spec["linhas"]:
        t = ln["t"].upper() if FONTE == "marker" else ln["t"]
        f = fm
        while dd.textlength(t, font=f) > w - 140:
            f = marker(f.size - 2)
        elementos.append(("linha", y, t, f, ln.get("destaque"), ln.get("sublinha")))
        y += int(f.size * 1.22) + (10 if ln.get("destaque") else 0)
    if spec.get("corpo"):
        fc = outfit(spec.get("tam_corpo", 34), 500)
        ls = quebra(spec["corpo"], fc, w - 150, dd)
        y += 18
        for l in ls:
            elementos.append(("corpo", y, l, fc))
            y += int(fc.size * 1.3)
    if spec.get("lista"):
        fl = outfit(spec.get("tam_corpo", 34), 600)
        y += 6
        for l in spec["lista"]:
            elementos.append(("corpo", y, l, fl))
            y += int(fl.size * 1.3)
    if spec.get("corpo2"):
        fc = outfit(spec.get("tam_corpo", 34), 500)
        y += 6
        for l in quebra(spec["corpo2"], fc, w - 150, dd):
            elementos.append(("corpo", y, l, fc))
            y += int(fc.size * 1.3)
    h = y + 50
    im = papelao(w, h).convert("RGBA")
    d = ImageDraw.Draw(im)
    for e in elementos:
        if e[0] == "num":
            cx, cy, r = w // 2, e[1] + 40, 42
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INK)
            fnum = marker(50)
            d.text((cx, cy + 2), str(spec["numero"]), font=fnum, fill=NUM_TXT, anchor="mm")
        elif e[0] == "linha":
            _, yy, t, f, dest, sub = e
            tw = d.textlength(t, font=f)
            x = (w - tw) / 2
            if dest:
                d.rectangle([x - 28, yy - 6, x + tw + 28, yy + f.size * 1.12], fill=TARJA)
                d.text((w / 2, yy + f.size * 0.55), t, font=f, fill=TARJA_TXT, anchor="mm")
            else:
                d.text((w / 2, yy + f.size * 0.55), t, font=f, fill=INK, anchor="mm")
            if sub:
                uy = yy + f.size * 1.25
                d.line([(x + tw * 0.15, uy), (x + tw * 0.82, uy)], fill=INK, width=7)
        else:
            _, yy, l, fc = e
            d.text((w / 2, yy + fc.size * 0.5), l, font=fc, fill=INK, anchor="mm")
    return im


def compor(spec, saida):
    random.seed(1)
    sign = placa(spec)
    ang = spec.get("angulo", 1.0)
    rot = sign.rotate(ang, resample=Image.BICUBIC, expand=True)
    topo = spec.get("topo_placa", 50)
    sx = (W - rot.width) // 2
    sign_bottom = topo + rot.height
    pill_h = 84
    foto_topo = sign_bottom + (pill_h + 40 if spec.get("passe") else 70) + spec.get("ajuste_foto", 0)
    bg = fundo(spec["foto"], foto_topo)
    # sombra
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    alpha = rot.split()[3].point(lambda p: 150 if p else 0)
    sombra = Image.new("RGBA", rot.size, (0, 0, 0, 255))
    sombra.putalpha(alpha)
    sh.paste(sombra, (sx + 6, topo + 16), sombra)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    bg = Image.alpha_composite(bg, sh)
    bg.paste(rot, (sx, topo), rot)
    d = ImageDraw.Draw(bg)
    if spec.get("passe"):
        px1, py1 = W - 70, sign_bottom - 18
        pw = 234
        d.rounded_rectangle([px1 - pw, py1, px1, py1 + pill_h], radius=26, fill=PILL)
        fp = outfit(25, 600)
        d.text((px1 - pw + 24, py1 + 16), "Passe para", font=fp, fill=PILL_TXT)
        d.text((px1 - pw + 24, py1 + 46), "o lado.", font=fp, fill=PILL_TXT)
        cx, cy = px1 - 38, py1 + pill_h // 2
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=PILL_TXT)
        d.text((cx, cy + 1), "→", font=outfit(26, 700), fill=PILL, anchor="mm")
    fr = outfit(24, 500)
    if spec.get("chamada"):
        d.text((40, H - 50), "↗ " + spec.get("chamada_txt", CHAMADA), font=fr, fill=(255, 255, 255), anchor="lm")
    d.text((W - 40, H - 50), HANDLE, font=fr, fill=(255, 255, 255), anchor="rm")
    bg.convert("RGB").save(saida, "PNG")


if __name__ == "__main__":
    specs = json.load(open(sys.argv[1]))
    marca = sys.argv[2] if len(sys.argv) > 2 else "pcd"
    set_brand(marca)
    if not FONTE:
        FONTE = "marker" if marca == "pcd" else "fraunces"
    for nome, spec in specs.items():
        compor(spec, nome)
        print("ok", nome)
