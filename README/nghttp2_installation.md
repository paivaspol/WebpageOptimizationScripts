# Building nghttp2 on Mac OS X El Capitan (10.11.3)

Installing nghttp2 on Mac OS X was a pain. Luckily, I have this [link](http://blog.kazuhooku.com/2014/11/memo-installing-nghttp2-onto-osx.html) that guided through most of the steps.
Basically, you would download necessary dependencies, `openssl`, `libev`, `zlib`, and `spdylay`, and build them.
Note that `libevent` library stated in the link was not the correct dependency. It was rather [libev](http://libev.schmorp.de). After building that, `nghttp2` configure script could not use `-lev` flag.
This was fixed by including `-L` and `-I` to the `LDFLAGS`, `CFLAGS`, and `CPPFLAGS`, where the path points to the build path.

At this point, I was able to run `make` to start building `nghttp2`. However, the build failed at one point where it couldn't find a symbol from `openssl`. The problem stems from
the build process of `openssl` where `make depend` couldn't find `stdargs.h`. After researching about this for a while, I gave up. The very hacky solution I used was 
install `openssl` via `Homebrew`, then copy everything under `[homebrew_openssl]\include` and `[homebrew-openssl]\lib` to the build path.

`make install` may complain about `PYTHONPATH` environment variable. Just `export PYTHONPATH=...` where `...` is the path is the one `make install` is mentioning`.

# Building nghttp2 on Ubuntu 14.04

It was much easier. Just follow the instructions [here](https://nghttp2.org/documentation/package_README.html#building-from-git) and everything should more or less work.
