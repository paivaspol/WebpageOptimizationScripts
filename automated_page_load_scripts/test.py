try:
    raise Exception('exection')
    print '0'
except Exception as e:
    print 'a'

print 'b'
