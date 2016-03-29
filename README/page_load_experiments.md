# Page Load Experiments

## Dependencies

* [nghttp2](http://nghttp2.org) use `nghttpx` with `-s` flag. The certificate should point to the local machine, `192.168.2.1`.
* [Squid](http://squid-cache.org) Enable SSL Bump.

## Installing Components

* [nghttp2](nghttp2_installation.md)
* [Squid](squid_installation.md)

## Setting up Squid for MITM

To perform a lower bound on the page load, where the network is the bottleneck, we need to cache all the contents, both
HTTP and HTTPS traffic, at the squid proxy. We need to generate a self-signed certificate for squid to use and have squid
operate with SSLBump enabled. Follow the [instructions](https://www.smoothnet.org/squid-v3-5-proxy-with-ssl-bump/) to generate
the self-signed certificate. Then, follow [instructions](
https://android.stackexchange.com/questions/61540/self-signed-certificate-install-claims-success-but-android-acts-as-if-cert-isn) 
to create the `.der` file, which is compatible on Android. Resign all the files from the first instructions using the steps
in the second instructions. Squid does not support `.der` file. Thus, we need to convert `.der` file to `.pem` file, which
can be done using `openssl x509 -inform der -in example.com.der.crt -out example.com.pem.crt` command. Make sure that the FQDN
is set to empty.

After generating the self-signed root CA, we need to install the self-signed root CA to the phone so that the certificate is
considered trusted and safe. First, copy the `.der` file over to the phone via `adb push` then install the certificate in
the security option under the Settings app. The certificate should appear under the user tab.

In `squid.conf`, point the certificate path to the full path of `example.com.pem.crt` and the key to the private key generated
from the second instruction. In addition, add the following lines to enable SSLBump:

```
ssl_bump stare all
ssl_bump bump all
```

An example of the configure script can be found [here](examples/squid.conf.example).
