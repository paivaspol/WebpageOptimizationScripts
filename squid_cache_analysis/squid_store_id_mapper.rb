#!/usr/bin/ruby

require "rubygems"
require 'syslog'

$patterns = {
  "^http(s)*:\/\/www\.google-analytics\.com\/r\/\_\_utm\.gif\?(.*)" => "http://www.google-analytics.com.squid.internal/r/__utm.gif",
  "^http(s)*:\/\/ssl\.google-analytics\.com\/r\/\_\_utm\.gif\?(.*)" => "http://www.google-analytics.com.squid.internal/r/__utm.gif",
  "^http:\/\/www\.google-analytics\.com\/collect\?(.*)" => "http://www.google-analytics.com.squid.internal/collect?",
  "^https:\/\/www\.google-analytics\.com\/collect\?(.*)" => "https://www.google-analytics.com.squid.internal/collect?",
  "^http(s)*:\/\/stats\.g\.doubleclick\.net\/r\/\_\_utm\.gif\?(.*)" => "http://stats.g.doubleclick.net.squid.internal/r/__utm.gif",
  "^http(s)*:\/\/pubads\.g\.doubleclick\.net\/gampad\/ad\?(.*)" => "http://pubads.g.doubleclick.net.squid.internal/gampad/ad?",
  "^http(s)*:\/\/googleads\.g\.doubleclick\.net\/pagead\/ads\?(.*)" => "http://googleads.g.doubleclick.net.squid.internal/pagead/ads?",
  "^http:\/\/googleads\.g\.doubleclick\.net\/pagead\/viewthroughconversion\/[0-9]+\/\?(.*)" => "http://googleads.g.doubleclick.net.squid.internal/pagead/viewthroughconversion/0/?",
  "^https:\/\/googleads\.g\.doubleclick\.net\/pagead\/viewthroughconversion\/[0-9]+\/\?(.*)" => "https://googleads.g.doubleclick.net.squid.internal/pagead/viewthroughconversion/0/?",
  "^http(s)*:\/\/ad\.doubleclick\.net\/ad\/(.*)" => "http://ad.doubleclick.net.squid.internal/ad/",
  "^http(s)*:\/\/ad\.doubleclick\.net\/ddm\/activity\/(.*)" => "http://ad.doubleclick.net.squid.internal/ddm/activity/",
  "^http(s)*:\/\/ad\.doubleclick\.net\/ddm\/ad\/.*" => "http://ad.doubleclick.net.squid.internal/ddm/ad/",
  "https:\/\/securepubads\.g\.doubleclick\.net\/gampad\/ads\?.*" => "https://securepubads.g.doubleclick.net/gampad/ads?",
  "https://stats.g.doubleclick.net/r/collect?.*" => "https://stats.g.doubleclick.net/r/collect?",
  "^http(s)*:\/\/[0-9]+\.fls\.doubleclick\.net\/activityi(.*)" => "http://0.fls.doubleclick.net.squid.internal/activityi",
  "^http(s)*:\/\/fls\.doubleclick\.net\/json\?(.*)" => "http://fls.doubleclick.net.squid.internal/json?",
  "^http(s)*:\/\/b\.scorecardresearch\.com\/b\?(.*)" => "http://b.scorecardresearch.com.squid.internal/b?",
  "^http(s)*:\/\/b\.scorecardresearch\.com\/p\?(.*)" => "http://b.scorecardresearch.com.squid.internal/p?",
  "^http:\/\/beacon\.scorecardresearch\.com\/scripts\/beacon.dll\?(.*)" => "http://beacon.scorecardresearch.com.squid.internal/scripts/beacon.dll?",
  "^http(s)*:\/\/sb\.scorecardresearch\.com\/b\?(.*)" => "http://sb.scorecardresearch.com.squid.internal/b?",
  "^http(s)*:\/\/sb\.scorecardresearch\.com\/beacon\?(.*)" => "http://sb.scorecardresearch.com.squid.internal/beacon?",
  "^http(s)*:\/\/sb\.scorecardresearch\.com\/p\?(.*)" => "http://sb.scorecardresearch.com.squid.internal/p?",
  "^http(s)*:\/\/[a-zA-Z0-9]+\.tt\.omtrdc\.net\/m2\/[a-zA-Z0-9]+\/mbox\/(standard)\?(.*)" => "http://0.tt.omtrdc.net.squid.internal/m2/0/mbox/standard?",
  "^http(s)*:\/\/[a-zA-Z0-9]+\.tt\.omtrdc\.net\/m2\/[a-zA-Z0-9]+\/mbox\/(ajax)\?(.*)" => "http://0.tt.omtrdc.net.squid.internal/m2/0/mbox/ajax?",
  "^http(s)*:\/\/jadserve\.postrelease\.com\/trk\.gif\?.*" => "http://jadserve.postrelease.com.squid.internal/trk.gif?",
  "https*:\/\/www\.facebook\.com\/impression\.php\/([a-zA-Z][0-9]*[a-zA-Z])\/\?.*" => "http://www.facebook.com.squid.internal/impression.php/0/?",
  "https*:\/\/www\.facebook\.com\/tr\/\?.*" => "http://www.facebook.com.squid.internal/tr/?",
  "https*:\/\/[0-9]+\.log\.optimizely\.com\/event\?.*" => "http://0.log.optimizely.com.squid.internal/event?",
  "https*:\/\/aax\.amazon\-adsystem\.com\/e\/dtb\/bid\?.*" => "http://aax.amazon-adsystem.com.squid.internal/e/dtb/bid?",
  "https*:\/\/assets\.pinterest\.com\/js\/pinit_main\.js\?.*" => "http://assets.pinterest.com.squid.internal/js/pinit_main.js?",
  "https*:\/\/c\.go\-mpulse\.net\/boomerang\/config\.js\?.*" => "http://c.go-mpulse.net.squid.internal/boomerang/config.js?",
  "https*:\/\/fls-na.amazon.com\/1\/batch\/1\/OP\/.*" => "http://fls-na.amazon.com.squid.internal/1/batch/1/OP/",
  "https*:\/\/global\.fncstatic\.com\/static\/v\/all\/js\/geo\.js" => "http://global.fncstatic.com.squid.internal/static/v/all/js/geo.js",
  "https*:\/\/ia\.media\-imdb\.com\/images\/G\/01\/vap\/video\/airy2\/\/prod\/2\.0\.1175\.0\/js\/airy\.ads\.\_TTW\_\.js\?.*" => "http://ia.media-imdb.com.squid.internal/images/G/01/vap/video/airy2//prod/2.0.1175.0/js/airy.ads._TTW_.js?",
  "https*:\/\/i\.imgur\.com\/lumbar\.gif\?.*" => "http://i.imgur.com.squid.internal/lumbar.gif?",
  "https*:\/\/nexus\.ensighten\.com\/[a-zA-Z]+\/[a-zA-Z]+\/serverComponent\.php\?.*" => "http://nexus.ensighten.com.squid.internal/homedepotmobile/prod/serverComponent.php?",
  "https*:\/\/pixel\.quantserve\.com\/pixel.*" => "http://pixel.quantserve.com.squid.internal/pixel",
  "https*:\/\/rtax.criteo.com\/delivery\/rta\/rta\.js\?.*" => "http://rtax.criteo.com.squid.internal/delivery/rta/rta.js?",
  "https*:\/\/secure\-[a-z][a-z]\.imrworldwide\.com\/cgi\-bin\/m\?.*" => "http://secure-us.imrworldwide.com.squid.internal/cgi-bin/m?",
  "https*:\/\/t2\.huluim\.com\/v3\/engagement\/browse\?.*" => "http://t2.huluim.com.squid.internal/v3/engagement/browse?",
  "https*:\/\/t2\.huluim\.com\/v3\/plustracking\/driverload\?.*" => "http://t2.huluim.com.squid.internal/v3/plustracking/driverload?",
  "https*:\/\/t2\.huluim\.com\/v3\/sitetracking\/pageload\?.*" => "http://t2.huluim.com.squid.internal/v3/sitetracking/pageload?",
  "https*:\/\/t2\.huluim\.com\/v3\/sitetracking\/session\?.*" => "http://t2.huluim.com.squid.internal/v3/sitetracking/session?",
  "https*:\/\/ads\.yieldmo\.com\/v002\/t\_ads\/ads\?.*" => "http://ads.yieldmo.com/v002/t_ads/ads?",
  "https*:\/\/weather\.com\/sites\/all\/modules\/glomo\/modules\/gm_footer\/gm_footer\.controller\.js\?.*" => "https://weather.com/sites/all/modules/glomo/modules/gm_footer/gm_footer.controller.js",
  "https*:\/\/trc\.taboola\.com\/aol\-aol\/log\/2\/debug\?.*" => "http://trc.taboola.com/aol-aol/log/2/debug?",
  "https*:\/\/trc\.taboola\.com\/aol\-aol\/trc\/3\/json\?.*" => "http://trc.taboola.com/aol-aol/trc/3/json?",
  "https*:\/\/wa\.and\.co\.uk\/b\/ss\/anddailymailprod\/1\/H\.26\/.*" => "http://wa.and.co.uk/b/ss/anddailymailprod/1/H.26/",
  "https*:\/\/b\.aol\.com\/vanity\/\?.*" => "http://b.aol.com/vanity/?",
  "https*:\/\/b\.aol\.com\/ping\?.*" => "http://b.aol.com/ping?",
  "https*:\/\/amplifypixel\.outbrain\.com\/pixel\?.*" => "https://amplifypixel.outbrain.com/pixel?"
}

def rewriter(request)
  $patterns.each do |pattern, substitute_url|
    case request
    when /#{pattern}/
      url = substitute_url
      return url
    when /^quit.*/
      exit 0
    end
  end
  return ""
end

def log(msg)
  Syslog.log(Syslog::LOG_ERR, "%s", msg)
end

def eval
  request = gets
  if (request && (request.match(/^[0-9]+\ /)))
    conc(request)
    return true
  else
    noconc(request)
    return false
  end
end


def conc(request)
  return if !request
  request = request.split
  if request[0] && request[1]
    log("original request [#{request.join(" ")}].") if $debug
    result = rewriter(request[1])
    if result
      url = request[0] +" OK store-id=" + result
    else
      url = request[0] +" ERR"
    end
    log("modified response [#{url}].") if $debug
    puts url
  else
    log("original request [had a problem].") if $debug
    url = request[0] + " ERR"
    log("modified response [#{url}].") if $debug
    puts url
  end

end

def noconc(request)
  return if !request
  request = request.split
  if request[0]
    log("Original request [#{request.join(" ")}].") if $debug
    result = rewriter(request[0])
    if result && (result.size > 10)
      url = "OK store-id=" + rewriter(request[0])
    else
      url = "ERR"
    end
    log("modified response [#{url}].") if $debug
    puts url
  else
    log("Original request [had a problem].") if $debug
    url = "ERR"
    log("modified response [#{url}].") if $debug
    puts url
  end
end

def validr?(request)
  if (request.ascii_only? && request.valid_encoding?)
    return true
  else
    STDERR.puts("errorness line#{request}")
    return false
  end
end

def main
  Syslog.open('new_helper.rb', Syslog::LOG_PID)
  log("Started")

  c = eval

  if c
    while request = gets
      conc(request) if validr?(request)
    end
  else
    while request = gets
      noconc(request) if validr?(request)
    end
  end
end

$debug = true
STDOUT.sync = true
main

