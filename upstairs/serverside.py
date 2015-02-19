import PIL
import os.path

red = redis.StrictRedis(host='localhost', port=6379, db=0)
#grab id_nums members of the 'inlab' set
id_nums = red.smembers('inlab')

#for each of the members, extract their photos from the db,
#resize them to thumbnail size, and put them in the ./photos
#directory

for id_num in id_nums:
    path = "photos/"+id_num+".jpg"
    if not os.path.exists(path):
        img = PIL.Image.fromstring('RGB',(1280,720),red.get(id_num+'.img'))
        img.thumbnail((300,169),PIL.Image.ANTIALIAS)
        img.save(path,'JPEG')



out = "<!DOCTYPE html><html><head><title>Members in the lab</title></head><body><h1>Members in the lab</h1>"
for id_num in id_nums:
    name =red.get(id_num+'.name')
    out += '<div><img src="photos/'+id_num+'.jpg"'+'alt="'+name+'" />'
    out += '<h2>'+name+'</h2></div>'

out += '</body></html>
