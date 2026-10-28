from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
G='/usr/share/fonts/truetype/google-fonts/'
W,H=1080,1920
GOLD=(222,184,98); CREAM=(248,243,232); MUTED=(196,188,172); INK=(10,9,7)
def F(k,sz):
    m={'b':'Poppins-Bold.ttf','bi':'Poppins-BoldItalic.ttf','m':'Poppins-Medium.ttf','mi':'Poppins-MediumItalic.ttf','l':'Poppins-Light.ttf','r':'Poppins-Regular.ttf','serif':'Lora-Variable.ttf','serifi':'Lora-Italic-Variable.ttf'}
    return ImageFont.truetype(G+m[k],sz)
def cover(p,fx=0.5,fy=0.5,dark=1.0,blur=0):
    im=ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    s=max(W/im.width,H/im.height); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    x=int((im.width-W)*fx); y=int((im.height-H)*fy); im=im.crop((x,y,x+W,y+H))
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    if dark!=1.0: im=ImageEnhance.Brightness(im).enhance(dark)
    return im
def plain():
    im=Image.new('RGB',(W,H),INK); g=Image.new('L',(W,H),0); d=ImageDraw.Draw(g)
    d.ellipse([(-300,-200),(1380,1100)],fill=60); g=g.filter(ImageFilter.GaussianBlur(220))
    return Image.composite(Image.new('RGB',(W,H),(58,44,20)),im,g)
def shade(im,top=(0,0),bot=(0,0)):
    g=Image.new('L',(1,H))
    for y in range(H):
        t=y/H;a=0
        if top[1] and t<top[1]: a=top[0]*(1-t/top[1])**1.2
        if bot[1] and t>bot[1]: a=max(a,bot[0]*((t-bot[1])/(1-bot[1]))**1.1)
        g.putpixel((0,y),int(255*a))
    return Image.composite(Image.new('RGB',(W,H),INK),im,g.resize((W,H)))
class Frame:
    def __init__(s,im,n,tot,brand=True):
        s.im=im; s.d=ImageDraw.Draw(s.im)
        if brand: s.d.text((80,150),'AUREAN AXIS',font=F('m',26),fill=GOLD)
        s.d.text((1000,150),f'{n}/{tot}',font=F('l',26),fill=CREAM,anchor='ra')
    def line(s,y,segs,sz,align='c',x0=80,lh=1.22):
        fonts=[F(k,sz) for _,k,*_ in segs]; ws=[s.d.textlength(t,font=f) for (t,*_),f in zip(segs,fonts)]
        x=x0 if align=='l' else (W-sum(ws))/2
        for seg,f,w in zip(segs,fonts,ws):
            t,k=seg[0],seg[1]; c=seg[2] if len(seg)>2 else (GOLD if k in('bi','mi','serifi') else CREAM)
            s.d.text((x,y),t,font=f,fill=c); x+=w
        return y+int(sz*lh)
    def lines(s,y,rows,sz,align='c',gap=0,**k):
        for r in rows: y=s.line(y,r if isinstance(r,list) else [(r,'b')],sz,align,**k)+gap
        return y
    def pill(s,y,text,w=560,sz=46):
        x1=(W-w)/2; s.d.rounded_rectangle([(x1,y),(x1+w,y+110)],radius=55,fill=GOLD)
        s.d.text((W/2,y+55),text,font=F('b',sz),fill=(16,13,8),anchor='mm'); return y+110
    def arrow(s,y,label='Keep tapping',x=80):
        s.d.text((x,y),label,font=F('m',34),fill=CREAM,anchor='lm'); e=x+s.d.textlength(label,font=F('m',34))+24
        s.d.line([(e,y+2),(e+100,y+2)],fill=GOLD,width=4); s.d.polygon([(e+100,y-10),(e+122,y+2),(e+100,y+14)],fill=GOLD)
    def card(s,y,title,body,x1=110,x2=970):
        s.d.rounded_rectangle([(x1,y),(x2,y+190)],radius=28,outline=GOLD,width=3,fill=(22,19,14))
        s.d.text((x1+40,y+40),title,font=F('b',46),fill=GOLD); s.d.text((x1+40,y+110),body,font=F('m',36),fill=CREAM); return y+190
    def small(s,y,text,c=MUTED,sz=28): s.d.text((W/2,y),text,font=F('r',sz),fill=c,anchor='ma')
    def dashed(s,box,label):
        x1,y1,x2,y2=box; dl=24
        for x in range(x1,x2,dl*2): s.d.line([(x,y1),(min(x+dl,x2),y1)],fill=GOLD,width=4); s.d.line([(x,y2),(min(x+dl,x2),y2)],fill=GOLD,width=4)
        for y in range(y1,y2,dl*2): s.d.line([(x1,y),(x1,min(y+dl,y2))],fill=GOLD,width=4); s.d.line([(x2,y),(x2,min(y+dl,y2))],fill=GOLD,width=4)
        s.d.text(((x1+x2)/2,(y1+y2)/2),label,font=F('m',34),fill=MUTED,anchor='mm')
def preview(paths,out):
    n=len(paths); pv=Image.new('RGB',(n*432+(n+1)*24,768+48),(18,16,14))
    for i,p in enumerate(paths): pv.paste(Image.open(p).resize((432,768),Image.LANCZOS),(24+i*456,24))
    pv.save(out,quality=88)
