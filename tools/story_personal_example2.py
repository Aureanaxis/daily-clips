import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit import *
A=sys.argv[2] if len(sys.argv)>2 else 'tools/story-photos'
def ph(n): return f'{A}/p{n:02d}.jpg'
T=4; fr=[]
def F_(im,n): return Frame(im,n,T,brand=False)
f=F_(shade(cover(ph(64),0.5,0.5),top=(0.92,0.42),bot=(0.6,0.8)),1)
f.lines(260,[[("Why I'm not like","b")],[('other ',"b"),('trading mentors',"bi")]],80); f.arrow(1760); fr.append(f)
f=F_(shade(cover(ph(36),0.5,0.5),top=(0.5,0.25),bot=(0.96,0.45)),2)
f.line(1240,[('I came from a trade','bi')],60)
y=f.lines(1340,[[('I was a welder.',"b")],[('Ran the best fabrication',"m")],[('company in West Yorkshire.',"m")]],52,gap=6)
f.lines(y+40,[[('No bank. No finance degree.',"b")],[('4 years and £65k of mistakes',"m")],[("so you don't have to make them.","m")]],48,gap=6); fr.append(f)
f=F_(shade(cover(ph(24),0.5,0.5),top=(0.5,0.25),bot=(0.96,0.45)),3)
f.line(1150,[('I trade live. ',"b"),('Every day.',"bi")],60)
f.lines(1260,[[('Same chart as my members.',"m")],[('Zones marked before the move.',"m")],[('Wins and losses on camera.',"m")],[('Nothing hidden.',"b")]],50,gap=8); fr.append(f)
f=F_(shade(cover(ph(34),0.5,0.35),top=(0.3,0.2),bot=(0.97,0.45)),4)
f.line(1060,[('The process, ',"b"),('not signals',"bi")],62)
y=f.lines(1160,[[('You learn why I take every entry,',"m")],[('not just copy it.',"m")]],46,gap=6)
y=f.lines(y+30,[[('I teach exactly how I trade',"b")],[('gold inside Aurean Axis.',"b")]],50)
y=f.pill(y+40,'Link in bio'); f.small(y+40,'Only risk what you can afford to lose.',CREAM,26); fr.append(f)
for i,fm in enumerate(fr,1): fm.im.save(f'{OUT}/different_{i}-of-{T}.png')
