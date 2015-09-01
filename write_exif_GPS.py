import tempfile
import os
import sys
import re
from fractions import Fraction


def main(focal, log_file):
    csv = open(log_file, 'r')
    tmp_file1 = tempfile.NamedTemporaryFile(delete=False)
    tmp_file2 = tempfile.NamedTemporaryFile(delete=False)

    count = 0
    images = []
    for line in csv.readlines():
        count += 1
        if count == 1:
            continue

        image, latitude, longitude, altitude, yaw, pitch, roll = line.split(',')
        image_name, ext = image.split('.')
        images.append(image_name + '.' + ext.lower())
        tmp_file1.write("{long} {lat} {alt}\n".format(long=longitude, lat=latitude, alt=altitude))
    tmp_file1.close()

    os.system('cs2cs +proj=latlong +datum=WGS84 +to +proj=latlong +datum=WGS84 < {inp} > {out}'.format(inp=tmp_file1.name, out=tmp_file2.name))
    os.remove(tmp_file1.name)

    count = 0
    for line in tmp_file2.readlines():
        lon, lat, h = line.split()
        h = str(Fraction(str(h))) if '/' in str(Fraction(str(h))) else str(Fraction(str(h))) + '/1'
        deglon, minslon, seclon, reflon = re.split('\'|"|d', lon)
	secfraclon = str(Fraction(seclon)) if '/' in str(Fraction(seclon)) else str(Fraction(seclon)) + '/1'
        deglat, minslat, seclat, reflat = re.split('\'|"|d', lat)
        secfraclat = str(Fraction(seclat)) if '/' in str(Fraction(seclat)) else str(Fraction(seclat)) + '/1'

        os.system('exiv2 -M"set Exif.GPSInfo.GPSLatitude {deglat}/1 {minslat}/1 {secfraclat}"'
		  ' -M"set Exif.GPSInfo.GPSLatitudeRef {reflat}" {image}'.format(deglat=deglat, minslat=minslat, secfraclat=secfraclat,
                                                                                 reflat=reflat, image=images[count]))

        os.system('exiv2 -M"set Exif.GPSInfo.GPSLongitude {deglon}/1 {minslon}/1 {secfraclon}"'
                  ' -M"set Exif.GPSInfo.GPSLongitudeRef {reflon}" {image}'.format(deglon=deglon, minslon=minslon, secfraclon=secfraclon,
                                                                                  reflon=reflon, image=images[count]))
        os.system('exiv2 -M"set Exif.GPSInfo.GPSAltitude {h}" {image}'.format(h=Fraction(h), image=images[count]))
        os.system('exiv2 -M"set Exif.GPSInfo.GPSAltitudeRef 0" {image}'.format(image=images[count]))
        os.system('exiv2 -M"set Exif.Photo.FocalLength {focal}" {image}'.format(focal=Fraction(str(focal)), image=images[count]))
        count +=1

    os.remove(tmp_file2.name)
    csv.close()


if __name__ == '__main__':
    focal = 0.0155171 * 1000
    log_file = sys.argv[-1]
    main(focal, log_file)
