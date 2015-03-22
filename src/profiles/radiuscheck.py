from math import sin, cos, radians, acos
from .models import ZipData, Location




def calc_dist_fixed(zip_b):
    """all angles in degrees, result in miles"""
    EARTH_RADIUS_IN_MILES = 3958.761
    locs = Location.objects.all()
    pickup_locs = []
    counter = 0
    for loc in locs:
        counter += 1
        zip_a = loc.zipcode
        allowable = float(loc.delivery_radius)
        
        lat_a = float(ZipData.objects.get(zipcode=zip_a).lat)
        long_a = float(ZipData.objects.get(zipcode=zip_a).long)
        
        lat_b = float(ZipData.objects.get(zipcode=zip_b).lat)
        long_b = float(ZipData.objects.get(zipcode=zip_b).long)
        
        lat_a = radians(lat_a)
        lat_b = radians(lat_b)
        delta_long = radians(long_a - long_b)
        cos_x = (
            sin(lat_a) * sin(lat_b) +
            cos(lat_a) * cos(lat_b) * cos(delta_long)
            )
        distance = round(acos(cos_x)*EARTH_RADIUS_IN_MILES,2)
        if distance > allowable:
            print 'out of range'
            valid = False
            print loc
            pickup_locs.append((loc,distance))

        else:
            print 'in range'
            print 'new location'
            valid = True
            return (True,int(loc.id))
            break
    if valid == False:
        a = min([x[1] for x in pickup_locs])
        dist = float(a)
        b = [place for (place, distance) in pickup_locs if distance == dist]
        return (False, int(b[0].id))
        
    print distance
    print 'distance: %s' % (acos(cos_x)*EARTH_RADIUS_IN_MILES)
    
    #return acos(cos_x) * EARTH_RADIUS_IN_MILES