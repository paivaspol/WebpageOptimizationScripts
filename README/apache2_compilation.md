# Apache2 Compilation

Compiling Apache2 was not a pain. The painful part is when it requires `mpm` to be included in the build. This has to be specfied as part of the `./configure` flag.
To enable all `mpm`s and `mod_http2` use the following configure command:

```
./configure --prefix='/home/ubuntu/build' --enable-http2 --with-nghttp2='/home/ubuntu/build' --enable-mpms-shared=all --enable-so --with-mpm=prefork
```
