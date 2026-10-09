import socket,ipaddress,http.client,ssl,hashlib
from urllib.parse import urlsplit
from html.parser import HTMLParser
class TextParser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in {'script','style'}:self.skip+=1
 def handle_endtag(self,t):
  if t in {'script','style'} and self.skip:self.skip-=1
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
def normalized_hash(t):return hashlib.sha256(' '.join(t.split()).encode()).hexdigest()
def fetch(url,allowed,max_bytes=2000000):
 u=urlsplit(url)
 if u.scheme!='https' or u.hostname not in allowed or u.username or u.password or u.port not in (None,443):raise ValueError('İzin verilmeyen URL')
 aa=socket.getaddrinfo(u.hostname,443,type=socket.SOCK_STREAM)
 if not aa or any(not ipaddress.ip_address(a[4][0]).is_global for a in aa):raise ValueError('Özel IP engellendi')
 ip=aa[0][4][0]
 class Pinned(http.client.HTTPSConnection):
  def connect(self):self.sock=self._context.wrap_socket(socket.create_connection((ip,443),timeout=self.timeout),server_hostname=self.host)
 conn=Pinned(u.hostname,timeout=20,context=ssl.create_default_context())
 try:
  conn.request('GET',(u.path or '/')+('?' + u.query if u.query else ''),headers={'User-Agent':'HibeRadari/0.1'})
  r=conn.getresponse()
  if r.status!=200:raise ValueError('HTTP '+str(r.status)+'; redirect otomatik izlenmez')
  data=r.read(max_bytes+1)
  if len(data)>max_bytes:raise ValueError('Boyut sınırı')
  mime=r.getheader('Content-Type','')
  if 'pdf' in mime or data.startswith(b'%PDF'):
   from pypdf import PdfReader
   from io import BytesIO
   pdf=PdfReader(BytesIO(data))
   if len(pdf.pages)>100:raise ValueError('Sayfa sınırı')
   text='\n'.join(f'Sayfa {i+1}: '+(p.extract_text() or '') for i,p in enumerate(pdf.pages))
  elif 'html' in mime:
   p=TextParser();p.feed(data.decode('utf-8',errors='replace'));text=' '.join(p.parts)
  else:raise ValueError('Belge tipi desteklenmiyor')
  if not text.strip():raise ValueError('Metin yok; manuel inceleme')
  return text,normalized_hash(text)
 finally:conn.close()
def parse_listing(html,marker,candidates,empty_marker=None):
 if marker not in html:raise ValueError('Parser yapısı değişti')
 if candidates:return {'status':'ok','count':len(candidates)}
 if empty_marker and empty_marker in html:return {'status':'empty_confirmed','count':0}
 raise ValueError('Sıfır ilan başarı değildir; kapsam kontrolü gerekli')
