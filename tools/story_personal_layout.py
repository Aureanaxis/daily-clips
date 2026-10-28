import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit import *
A,OUT=sys.argv[1],sys.argv[2]; os.makedirs(OUT,exist_ok=True)
def ph(n): return f'{A}/p{n:02d}_i.jpeg'
T=4; fr=[]
def F_(im,n): return Frame(im,n,T,brand=False)
f=F_(shade(cover(ph(14),0.55,0.5),top=(0.9,0.42),bot=(0.6,0.8)),1)
f.lines(290,[[('A day in my life',"b")],[('as a ',"b"),('gold trader',"bi")]],84); f.arrow(1760); fr.append(f)
f=F_(shade(cover(ph(30),0.6,0.5),top=(0.6,0.3),bot=(0.95,0.5)),2)
f.line(1300,[('Morning',"bi")],62)
f.lines(1400,[[('Charts before anything else.',"b")],[('Mark the zones.',"m")],[('Set the plan.',"m")]],58,gap=6); fr.append(f)
f=F_(shade(cover(ph(34),0.5,0.5),top=(0.6,0.3),bot=(0.95,0.5)),3)
f.line(1300,[('Session time',"bi")],62)
f.lines(1400,[[('Live with my students.',"b")],[('Same chart. Same entries.',"m")],[('Questions answered in real time.',"m")]],56,gap=6); fr.append(f)
f=F_(shade(cover(ph(6),0.55,0.4),top=(0.5,0.25),bot=(0.97,0.45)),4)
f.line(1080,[('Evening',"bi")],62)
y=f.lines(1180,[[('No boss. No commute.',"b")],[('Just a ',"b"),('plan',"bi"),('.',"b")]],70)
y=f.lines(y+20,[[('I teach exactly how I trade',"m")],[('gold inside Aurean Axis.',"m")]],44)
y=f.pill(y+40,'Link in bio'); f.small(y+40,'Only risk what you can afford to lose.',CREAM,26); fr.append(f)
for i,fm in enumerate(fr,1): fm.im.save(f'{OUT}/day_{i}-of-{T}.png')
pv=Image.new('RGB',(T*226,400)); [pv.paste(Image.open(f'{OUT}/day_{i}-of-{T}.png').resize((216,384)),((i-1)*226,8)) for i in range(1,T+1)]; pv.save(OUT+'/../today_check.jpg')
