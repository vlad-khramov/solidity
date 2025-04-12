#! /usr/bin/env python3
import random
import re
import os
import getopt
import sys
from os import path
import tempfile
import subprocess

ENCODING = "utf-8"
SOURCE_FILE_PATTERN = r"\b\d+_error\b"

# default branch for pull requests
PR_DEFAULT_BRANCH = 'origin/develop'

# Error IDs that were previously used but have been removed from the code. They should not be reused.
REMOVED_IDS = {
    "1054", # liblangutil/ParserBase.cpp, 0203eea20e6e0ace5cc4b4a0d552eedffce2f881
    "1054", # liblangutil/ParserBase.cpp, 0ee4a85a841f6494c16a93bd60f3a9ec1a7f2c6e
    "1054", # liblangutil/ParserBase.cpp, 34543e5eab30a8e0632e9b78784fc31dd5bfc56d
    "1054", # liblangutil/ParserBase.cpp, b3b1df65567b0f7497202de4c67271505129ad9a
    "1054", # liblangutil/ParserBase.cpp, cb2c9823c7d91708d0ed15bc55fa14c5a1e4999d
    "1054", # liblangutil/ParserBase.cpp, ea38ff034868fa975314c38f9f4cd19e12285848
    "1054", # liblangutil/ParserBase.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "1054", # liblangutil/ParserBase.cpp, ff0ec61e1ee9cd04097d5705f7fa803278e811bd
    "1093", # libsolidity/analysis/TypeChecker.cpp, 5fedb4eab00ad4829490be6f7fd82a33f7bafeed
    "1093", # libsolidity/analysis/TypeChecker.cpp, 894478ff8c9c0a6d5ffa091fe66adf560e9c6437
    "1093", # libsolidity/analysis/TypeChecker.cpp, 936ea6f950ffd9b4d4bfaa9cd5ae949be0df58fd
    "1093", # libsolidity/formal/SMTEncoder.cpp, 0203eea20e6e0ace5cc4b4a0d552eedffce2f881
    "1093", # libsolidity/formal/SMTEncoder.cpp, 11a7763f492411d1fb77841caa48fd918dca64d4
    "1093", # libsolidity/formal/SMTEncoder.cpp, 20efba6b55fbe158c89e28d59486110ead324480
    "1093", # libsolidity/formal/SMTEncoder.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "1093", # libsolidity/formal/SMTEncoder.cpp, fdc4142b2c13c891092d1ec95209dbe94dd3e51d
    "1093", # libsolidity/formal/SMTEncoder.cpp, ff0ec61e1ee9cd04097d5705f7fa803278e811bd
    "1123", # libsolidity/analysis/TypeChecker.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "1123", # libsolidity/analysis/TypeChecker.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "1123", # libsolidity/analysis/TypeChecker.cpp, 7ac440f35b3b2aa7fb9958c01d63789a5ff53964
    "1123", # libsolidity/analysis/TypeChecker.cpp, 7f15be5549c990f86e38002d20eb0d6abcfc3186
    "1123", # libsolidity/analysis/TypeChecker.cpp, fd9050614a6089168bd4565f4b49c64d04a0ef71
    "1147", # libsolidity/formal/CHC.cpp, 241a564fcabb40b829b2ba497dd87d488b83fbb9
    "1147", # libsolidity/formal/CHC.cpp, 2dd693b893a9b7a1834352381a2e92c807b0d9e6
    "1147", # libsolidity/formal/CHC.cpp, 53d497fc31a219242a80689bdee4a9f904f8ae2d
    "1147", # libsolidity/formal/CHC.cpp, 694ec92688617a876d1f1d97beba6ca1b52e6906
    "1147", # libsolidity/formal/CHC.cpp, 81cdc39f51e08f9c98af54548833fe71f909bc52
    "1147", # libsolidity/formal/CHC.cpp, 9605b85c210960496dd842ae07b4bc1e929d0c06
    "1147", # libsolidity/formal/CHC.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "1147", # libsolidity/formal/CHC.cpp, ee9a03ffe11f3ea1b6f4ce31e3aa865e0e9f34d2
    "1220", # libsolidity/analysis/TypeChecker.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "1220", # libsolidity/analysis/TypeChecker.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "1220", # libsolidity/analysis/TypeChecker.cpp, 7ac440f35b3b2aa7fb9958c01d63789a5ff53964
    "1220", # libsolidity/analysis/TypeChecker.cpp, 7f15be5549c990f86e38002d20eb0d6abcfc3186
    "1220", # libsolidity/analysis/TypeChecker.cpp, fd9050614a6089168bd4565f4b49c64d04a0ef71
    "1273", # libsolidity/analysis/TypeChecker.cpp, 3f14c904b08a358fe1b039519445439eb37d8f37
    "1273", # libsolidity/analysis/TypeChecker.cpp, 6979952995be760d4f22153b85d3addd1fd70aaf
    "1273", # libsolidity/analysis/TypeChecker.cpp, 6c9db334c6b930675c849f6fe459c900a0e469d7
    "1273", # libsolidity/analysis/TypeChecker.cpp, db4dd51739bcda262218f118611c17faac8c136b
    "1273", # libsolidity/analysis/TypeChecker.cpp, eedd12ad1d3024a82f7a4eade14f10f6d2a4af18
    "1574", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "1574", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "1665", # libsolidity/analysis/DeclarationTypeChecker.cpp, 3f14c904b08a358fe1b039519445439eb37d8f37
    "1665", # libsolidity/analysis/DeclarationTypeChecker.cpp, 6979952995be760d4f22153b85d3addd1fd70aaf
    "1665", # libsolidity/analysis/DeclarationTypeChecker.cpp, 6c9db334c6b930675c849f6fe459c900a0e469d7
    "1665", # libsolidity/analysis/DeclarationTypeChecker.cpp, db4dd51739bcda262218f118611c17faac8c136b
    "1665", # libsolidity/analysis/DeclarationTypeChecker.cpp, eedd12ad1d3024a82f7a4eade14f10f6d2a4af18
    "1719", # libsolidity/analysis/TypeChecker.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "1719", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "1719", # libsolidity/analysis/TypeChecker.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "1719", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "1719", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "1719", # libsolidity/analysis/TypeChecker.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "1719", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "1719", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "1719", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "1719", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "1719", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "1733", # libyul/AsmAnalysis.cpp, 0d0f2771654b14ee0e8d317a5eb22dbff8eab332
    "1733", # libyul/AsmAnalysis.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "1733", # libyul/AsmAnalysis.cpp, 664ee2327d24ffb89f6632a2aff12fa28743b839
    "1950", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "1950", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "1950", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "1950", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "1950", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "1957", # liblangutil/ParserBase.cpp, 6965f199fd11cada51c5a97ceb72cc5e14534a17
    "1957", # liblangutil/ParserBase.cpp, 9adbced98e49588bcc29e181f2560c2eadaa22ac
    "1957", # liblangutil/ParserBase.cpp, c43c3c3a3ad68fa0e47edda3df34d717193fde37
    "1957", # liblangutil/ParserBase.cpp, c703b5cd8ceeee3add715100ca04d2ae76c33609
    "2138", # libsolidity/experimental/analysis/TypeInference.cpp, 1906cf13c1308ed88f8ec102489d6d0d933f8090
    "2138", # libsolidity/experimental/analysis/TypeInference.cpp, fb99132474c177fc861305feeafd43b9cbb93b66
    "2177", # libsolidity/formal/SMTEncoder.cpp, 0ea4bdafcd881aa55dd3bb1ad0f8a3f38ea9d47e
    "2177", # libsolidity/formal/SMTEncoder.cpp, 466b05398ff8a0f6c8b0e326b9a7150111d167f7
    "2177", # libsolidity/formal/SMTEncoder.cpp, 4b342a7cadd752c48bd6b8c8963d9019141a0fd9
    "2177", # libsolidity/formal/SMTEncoder.cpp, 52f9db141bbf5fe06281366279c3352d5195109f
    "2177", # libsolidity/formal/SMTEncoder.cpp, 56d68552228d74ef36c50ec44a34e2e50105c49d
    "2177", # libsolidity/formal/SMTEncoder.cpp, 6c9db334c6b930675c849f6fe459c900a0e469d7
    "2177", # libsolidity/formal/SMTEncoder.cpp, 9b1f90512be6fb3ffcf7cbea1598ee7ed2296951
    "2177", # libsolidity/formal/SMTEncoder.cpp, abfa136afb9ff260c829f7bbe89821afe845a6f4
    "2177", # libsolidity/formal/SMTEncoder.cpp, e23d8f559370f5aa740782d22048a1d16fd6e4aa
    "2314", # liblangutil/ParserBase.cpp, 6965f199fd11cada51c5a97ceb72cc5e14534a17
    "2332", # libsolidity/analysis/TypeChecker.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "2332", # libsolidity/analysis/TypeChecker.cpp, 552a5f0913d97e96a423982613abdcbcf96b271a
    "2332", # libsolidity/analysis/TypeChecker.cpp, 9eda69f637b744a9519e31735aa4c25ab94fca1e
    "2332", # libsolidity/analysis/TypeChecker.cpp, c6281f29d5eb5654158dc4758da8b8b586e058bb
    "2332", # libsolidity/analysis/TypeChecker.cpp, de515313662c1db38bc2f9b5ef2e132b43020a0f
    "2332", # libsolidity/analysis/TypeChecker.cpp, e7a6534d4f34e1333bc34f17031997e495fc7f90
    "2332", # libsolidity/analysis/TypeChecker.cpp, efe829b4b27805c14b4c97e6e14a73273a522152
    "2370", # libsolidity/analysis/TypeChecker.cpp, 2665eaa4fac3d249fa3d892487ed7b5cfd562e49
    "2370", # libsolidity/analysis/TypeChecker.cpp, 9f0a6319484c9ff39b8986a9f06cf3a7ab6e1f52
    "2370", # libsolidity/analysis/TypeChecker.cpp, a7db4fa4a5b49b3285d41b0cef8faa0b83b70dc5
    "2450", # libyul/AsmAnalysis.cpp, 1f49edd29d398795660770c4514065d7dfb1bcd4
    "2450", # libyul/AsmAnalysis.cpp, 259292c8846ab6af36810e0aef3bb62de1e22d59
    "2450", # libyul/AsmAnalysis.cpp, 6b3171c38b6b20dbb4a84ca73a562edfc60f7493
    "2450", # libyul/AsmAnalysis.cpp, 9820df58abfe918c5f92c6d4fa066e2da5c3bf35
    "2450", # libyul/AsmAnalysis.cpp, d12db7ec5202b1406bc0e6c4537a4f3def7d7d64
    "2450", # libyul/AsmAnalysis.cpp, f97b376f7e2a8cdf386c12a55bc949d67fabb3e2
    "2657", # libyul/AsmAnalysis.cpp, 7ac440f35b3b2aa7fb9958c01d63789a5ff53964
    "2657", # libyul/AsmAnalysis.cpp, 859220c9bd84b766774358eeb4feb16978de8fb0
    "2657", # libyul/AsmAnalysis.cpp, ded5d721d2c97170905a536b1f996b79045c84d1
    "2658", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "2658", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "2658", # libsolidity/experimental/analysis/TypeInference.cpp, 1906cf13c1308ed88f8ec102489d6d0d933f8090
    "2658", # libsolidity/experimental/analysis/TypeInference.cpp, fb99132474c177fc861305feeafd43b9cbb93b66
    "2683", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "2683", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "2683", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "2683", # libsolidity/formal/SMTEncoder.cpp, bd0c46abf55cd6d3beae62bd1618ad8463b4e88b
    "2683", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "2718", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "2718", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "2837", # libsolidity/parsing/Parser.cpp, 11b227e33e8c8267fbf5218105c82709fc310023
    "2837", # libsolidity/parsing/Parser.cpp, 14d2170b4697ce8a1a1600e7b91534651241ac62
    "2837", # libsolidity/parsing/Parser.cpp, 2abd3073d43da89b06c3ed3c03f4f5ab2c39c0da
    "2837", # libsolidity/parsing/Parser.cpp, 39e3da19053fb4d892e1aba2de9ba7a5c225f68f
    "2837", # libsolidity/parsing/Parser.cpp, 69411436139acf5dbcfc5828446f18b9fcfee32c
    "2837", # libsolidity/parsing/Parser.cpp, 81c7b30a6a3cbce6fa01c6f405b0eff90883b3e8
    "2837", # libsolidity/parsing/Parser.cpp, f9b23ca845cd90072b21e550c8ee857b5f095888
    "2923", # libsolidity/formal/SMTEncoder.cpp, 4b342a7cadd752c48bd6b8c8963d9019141a0fd9
    "2923", # libsolidity/formal/SMTEncoder.cpp, 6c9db334c6b930675c849f6fe459c900a0e469d7
    "2923", # libsolidity/formal/SMTEncoder.cpp, 875dc0f10c63a7caa00081cb2c7e6adbce6922fb
    "2923", # libsolidity/formal/SMTEncoder.cpp, 87e1934beecae96f9ce7d7381070c42956407f76
    "2923", # libsolidity/formal/SMTEncoder.cpp, b401093679a171d18c4a2b4aaa59057f75ee0618
    "2923", # libsolidity/formal/SMTEncoder.cpp, c8cc73c80c994f84563ac474a455521d38fbcc8f
    "3263", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "3263", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "3263", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "3263", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "3263", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, 21489d8193a82506b3b4f54181157da2b7ba877d
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, 221524b153193f92fed086db391424e938735b69
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, 4a720a65112d8e5d65bda55fb10594b615c453d4
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, 4dd25f73027b3a8c6de01565a837d6f6d3c50fbe
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, ad311fae1902cf3159834de6d494b46386d0cede
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "3299", # libsolidity/analysis/SyntaxChecker.cpp, ff0ec61e1ee9cd04097d5705f7fa803278e811bd
    "3312", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "3312", # libsolidity/analysis/TypeChecker.cpp, 3e3f9a472f061ed74e91b77259c7b7c3085cb1c1
    "3312", # libsolidity/analysis/TypeChecker.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "3312", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "3312", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "3312", # libsolidity/analysis/TypeChecker.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "3312", # libsolidity/analysis/TypeChecker.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "3312", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "3312", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "3312", # libsolidity/analysis/TypeChecker.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "3312", # libsolidity/analysis/TypeChecker.cpp, a79d7c158837f31319a789ad256b81deec6135e5
    "3312", # libsolidity/analysis/TypeChecker.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "3312", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "3312", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "3312", # libsolidity/analysis/TypeChecker.cpp, d41eaeba5686828b85279057f3a7da8be0f9a8f9
    "3312", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "3312", # libsolidity/analysis/TypeChecker.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "3347", # liblangutil/ParserBase.cpp, 9adbced98e49588bcc29e181f2560c2eadaa22ac
    "3347", # liblangutil/ParserBase.cpp, c43c3c3a3ad68fa0e47edda3df34d717193fde37
    "3347", # liblangutil/ParserBase.cpp, c703b5cd8ceeee3add715100ca04d2ae76c33609
    "3408", # libsolidity/analysis/TypeChecker.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "3408", # libsolidity/analysis/TypeChecker.cpp, 552a5f0913d97e96a423982613abdcbcf96b271a
    "3408", # libsolidity/analysis/TypeChecker.cpp, 9eda69f637b744a9519e31735aa4c25ab94fca1e
    "3408", # libsolidity/analysis/TypeChecker.cpp, c6281f29d5eb5654158dc4758da8b8b586e058bb
    "3408", # libsolidity/analysis/TypeChecker.cpp, de515313662c1db38bc2f9b5ef2e132b43020a0f
    "3408", # libsolidity/analysis/TypeChecker.cpp, e7a6534d4f34e1333bc34f17031997e495fc7f90
    "3408", # libsolidity/analysis/TypeChecker.cpp, efe829b4b27805c14b4c97e6e14a73273a522152
    "3442", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "3442", # libsolidity/analysis/TypeChecker.cpp, 3e3f9a472f061ed74e91b77259c7b7c3085cb1c1
    "3442", # libsolidity/analysis/TypeChecker.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "3442", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "3442", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "3442", # libsolidity/analysis/TypeChecker.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "3442", # libsolidity/analysis/TypeChecker.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "3442", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "3442", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "3442", # libsolidity/analysis/TypeChecker.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "3442", # libsolidity/analysis/TypeChecker.cpp, a79d7c158837f31319a789ad256b81deec6135e5
    "3442", # libsolidity/analysis/TypeChecker.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "3442", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "3442", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "3442", # libsolidity/analysis/TypeChecker.cpp, d41eaeba5686828b85279057f3a7da8be0f9a8f9
    "3442", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "3442", # libsolidity/analysis/TypeChecker.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "3478", # libsolidity/analysis/TypeChecker.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "3478", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "3478", # libsolidity/analysis/TypeChecker.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "3478", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "3478", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "3478", # libsolidity/analysis/TypeChecker.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "3478", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "3478", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "3478", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "3478", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "3478", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, 0004ad876451e28de1b3aa031ab56d08d2cdb3b1
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, 07d1bc5f37ab071ec8a33d98f663462ce83c38ea
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, 79e9d619a3dab9117a685c528edb7f195ea2c79e
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, 7a5be4a063afc2f4eaf0519123a5d2cc7bae0f5d
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, b6dbfdf79b9592658cbe23f1e93726454024fc4a
    "3530", # libsolidity/analysis/DeclarationTypeChecker.cpp, e8c628e6ccd04392fb2e639e290c1c3e3948dbb1
    "3625", # libsolidity/analysis/TypeChecker.cpp, 52c49aebe80ada117f3244e73eb5e643bbbfafe1
    "3625", # libsolidity/analysis/TypeChecker.cpp, d50676ecb0a15dff6cf9b106b9cb0422f9b62123
    "3672", # libyul/AsmAnalysis.cpp, 241a564fcabb40b829b2ba497dd87d488b83fbb9
    "3672", # libyul/AsmAnalysis.cpp, 291c00c3decd89f3338777ce8836a974b216cd2a
    "3672", # libyul/AsmAnalysis.cpp, 655113e922675cb06d69fa1e7c364eb99e58eb67
    "3672", # libyul/AsmAnalysis.cpp, 7da82534d432403f107ff3cdb9e9e20c197cbf27
    "3672", # libyul/AsmAnalysis.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "3682", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "3682", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "3682", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "3682", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "3682", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "3772", # libyul/AsmParser.cpp, 0cc0cabd30a0eb6328a59f7df79f23ae41013f56
    "3772", # libyul/AsmParser.cpp, 2856f565256cebe58e9ebfe9bdbe1fc383c11d41
    "3772", # libyul/AsmParser.cpp, 680ea78f14c31d953555838ebbc3ea484f3e55e5
    "3772", # libyul/AsmParser.cpp, 7eb5e27e54c3ffc0e0a1e6d9b6c50e992df6886b
    "3772", # libyul/AsmParser.cpp, f04adde6641b09c8744fb1576eda87657b4d9a2d
    "3781", # libyul/AsmAnalysis.cpp, 0d0f2771654b14ee0e8d317a5eb22dbff8eab332
    "3781", # libyul/AsmAnalysis.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "3781", # libyul/AsmAnalysis.cpp, 664ee2327d24ffb89f6632a2aff12fa28743b839
    "3796", # liblangutil/ParserBase.cpp, 9adbced98e49588bcc29e181f2560c2eadaa22ac
    "3796", # liblangutil/ParserBase.cpp, c43c3c3a3ad68fa0e47edda3df34d717193fde37
    "3796", # liblangutil/ParserBase.cpp, c703b5cd8ceeee3add715100ca04d2ae76c33609
    "3876", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "3876", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "3876", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "3876", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "3876", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "3881", # libsolidity/analysis/ReferencesResolver.cpp, 66a8c7d1ab5b744736d1355ba46c9e1d5f090ac8
    "3947", # libyul/AsmAnalysis.cpp, 0d0f2771654b14ee0e8d317a5eb22dbff8eab332
    "3947", # libyul/AsmAnalysis.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "3947", # libyul/AsmAnalysis.cpp, 664ee2327d24ffb89f6632a2aff12fa28743b839
    "3969", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "3969", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "3978", # libsolidity/analysis/TypeChecker.cpp, 253889cbf17a980c24e0ff97476c85edb84a2496
    "3978", # libsolidity/analysis/TypeChecker.cpp, 36f93921540d12fb4250f699e7bfaf804f1e3363
    "3978", # libsolidity/analysis/TypeChecker.cpp, 5da6bddccbbce7f1ccd0d270ecb9e4d13e58d95e
    "3978", # libsolidity/analysis/TypeChecker.cpp, 61425e354112c061c4d95c4a14486d2ae7a2e03d
    "3978", # libsolidity/analysis/TypeChecker.cpp, ee657f53612b987eaf257d5e5698e80b12defe59
    "3978", # libsolidity/analysis/TypeChecker.cpp, fda352094f0e9f586004dda48daef9788068f523
    "3997", # libsolidity/analysis/SyntaxChecker.cpp, 9adbced98e49588bcc29e181f2560c2eadaa22ac
    "3997", # libsolidity/analysis/SyntaxChecker.cpp, c43c3c3a3ad68fa0e47edda3df34d717193fde37
    "3997", # libsolidity/analysis/SyntaxChecker.cpp, c703b5cd8ceeee3add715100ca04d2ae76c33609
    "4035", # libsolidity/analysis/TypeChecker.cpp, 3e3065ac00bf835cc669120b74b24e00361dc767
    "4035", # libsolidity/analysis/TypeChecker.cpp, 5fedb4eab00ad4829490be6f7fd82a33f7bafeed
    "4035", # libsolidity/analysis/TypeChecker.cpp, 849b16babb372aa9fc4722114c0a46881da9e010
    "4035", # libsolidity/analysis/TypeChecker.cpp, 894478ff8c9c0a6d5ffa091fe66adf560e9c6437
    "4035", # libsolidity/analysis/TypeChecker.cpp, 936ea6f950ffd9b4d4bfaa9cd5ae949be0df58fd
    "4035", # libsolidity/analysis/TypeChecker.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "4035", # libsolidity/analysis/TypeChecker.cpp, b9f2697a3c86f32aada10323f1750bde8bea06bc
    "4130", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "4130", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "4224", # libsolidity/analysis/TypeChecker.cpp, 5433a640fb97efe90e29c98ed71c4e59afac788b
    "4224", # libsolidity/analysis/TypeChecker.cpp, 6f3095a1994ffdce7dc1c94cbe5849d9a9cd5daf
    "4224", # libsolidity/analysis/TypeChecker.cpp, 78d94737a46b35fbf965fa80a69d5a9b762dca8c
    "4224", # libsolidity/analysis/TypeChecker.cpp, 851051c64a79f9a3c84d1c66fdb400cb1c66d271
    "4224", # libsolidity/analysis/TypeChecker.cpp, 99a9bd1a63fc198ed953e2702b5795b58311b1a7
    "4224", # libsolidity/analysis/TypeChecker.cpp, b605211d538b4a5f2617da95743d04fada251e80
    "4224", # libsolidity/analysis/TypeChecker.cpp, e590a99f399e0be33dfba0ab63065d7f17e1e870
    "4316", # libyul/AsmAnalysis.cpp, 375cb09341743262bff950c4c8953fc9ab9fd711
    "4316", # libyul/AsmAnalysis.cpp, 5ef660b17abaa6f9e3b0dd8a949268806ececcd4
    "4316", # libyul/AsmAnalysis.cpp, 67ebb206eab4863d47f67ed219ee4dbaa985819f
    "4316", # libyul/AsmAnalysis.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "4316", # libyul/AsmAnalysis.cpp, a09a79199968363f777cc9a4470b30278dc32507
    "4316", # libyul/AsmAnalysis.cpp, d67862362a16f03906386d2d2cb4d12e586d6b73
    "4579", # libsolidity/analysis/TypeChecker.cpp, 5433a640fb97efe90e29c98ed71c4e59afac788b
    "4579", # libsolidity/analysis/TypeChecker.cpp, 6f3095a1994ffdce7dc1c94cbe5849d9a9cd5daf
    "4579", # libsolidity/analysis/TypeChecker.cpp, 78d94737a46b35fbf965fa80a69d5a9b762dca8c
    "4579", # libsolidity/analysis/TypeChecker.cpp, 851051c64a79f9a3c84d1c66fdb400cb1c66d271
    "4579", # libsolidity/analysis/TypeChecker.cpp, 99a9bd1a63fc198ed953e2702b5795b58311b1a7
    "4579", # libsolidity/analysis/TypeChecker.cpp, b605211d538b4a5f2617da95743d04fada251e80
    "4579", # libsolidity/analysis/TypeChecker.cpp, e590a99f399e0be33dfba0ab63065d7f17e1e870
    "4599", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "4599", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "4626", # libsolidity/analysis/TypeChecker.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "4626", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "4626", # libsolidity/analysis/TypeChecker.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "4626", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "4626", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "4626", # libsolidity/analysis/TypeChecker.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "4626", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "4626", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "4626", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "4626", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "4626", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "4639", # libsolidity/formal/SMTEncoder.cpp, 36f93921540d12fb4250f699e7bfaf804f1e3363
    "4639", # libsolidity/formal/SMTEncoder.cpp, 80d743426f7c7da5e55423f6a3223145bf75b559
    "4639", # libsolidity/formal/SMTEncoder.cpp, 91c88a5f6b9569d9b5d2ee9ad375ba9312c310fa
    "4639", # libsolidity/formal/SMTEncoder.cpp, a0a02f2307e4efac342da04cb99302723856d5c3
    "4639", # libsolidity/formal/SMTEncoder.cpp, cbfd47cc9a7cf605d848f9e0ddd1f8473492c90c
    "4639", # libsolidity/formal/SMTEncoder.cpp, ee657f53612b987eaf257d5e5698e80b12defe59
    "4639", # libsolidity/formal/SMTEncoder.cpp, f313668ef16d6491eda9de6bb3ba30a46991c8d6
    "4686", # libsolidity/experimental/analysis/TypeInference.cpp, 4577aebfd24a8dec47f7ce085d4e8887f5b8b3af
    "4686", # libsolidity/experimental/analysis/TypeInference.cpp, fce70ef0e34b7e6cc8d22b0fc08784758503e8d7
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, 241a564fcabb40b829b2ba497dd87d488b83fbb9
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, 73506e285875c98874cb0fb92168a17822ddb449
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, 9e5a56a6491a250ac455f51c6ccd1941d7f44537
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, aea75d0f5b2163c6b40fe8e1c4206bf8261137b2
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, d31f05fcc062b7242412086c70dc9ccf357be86f
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "4794", # libsolidity/analysis/ReferencesResolver.cpp, ffdb0e37ff788afdf54ea1224a8c8184043322f9
    "5073", # libsolidity/analysis/NameAndTypeResolver.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "5073", # libsolidity/analysis/NameAndTypeResolver.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "5073", # libsolidity/analysis/NameAndTypeResolver.cpp, 8de2686dd2f071e3b30925f9a7e28669b72e66fd
    "5073", # libsolidity/analysis/NameAndTypeResolver.cpp, efe319998110068b8bd3152230a6ff5d0a2339f1
    "5084", # libsolidity/formal/SMTEncoder.cpp, 046cc4212120a47a835183999259c837bee0bf9b
    "5084", # libsolidity/formal/SMTEncoder.cpp, 431397eddf43bf71274c4a8c00aea2acbaec723d
    "5084", # libsolidity/formal/SMTEncoder.cpp, 4b342a7cadd752c48bd6b8c8963d9019141a0fd9
    "5084", # libsolidity/formal/SMTEncoder.cpp, 6796ce7947b4e39b76717689170f9d89bbb62c62
    "5084", # libsolidity/formal/SMTEncoder.cpp, 6c9db334c6b930675c849f6fe459c900a0e469d7
    "5084", # libsolidity/formal/SMTEncoder.cpp, 7417965ae3efc3078159741c2bad0427bb97fc01
    "5084", # libsolidity/formal/SMTEncoder.cpp, 756e21a8883e8570c6af233f9a0fcf74d6b7c78f
    "5084", # libsolidity/formal/SMTEncoder.cpp, b401093679a171d18c4a2b4aaa59057f75ee0618
    "5084", # libsolidity/formal/SMTEncoder.cpp, fedbea46cda1d67f00212e2d3ca51e34b8061076
    "5170", # libyul/AsmAnalysis.cpp, 0d0f2771654b14ee0e8d317a5eb22dbff8eab332
    "5170", # libyul/AsmAnalysis.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "5170", # libyul/AsmAnalysis.cpp, 664ee2327d24ffb89f6632a2aff12fa28743b839
    "5256", # libsolidity/analysis/DocStringTagParser.cpp, 354f9d101530d38faaeaaf12382bf95e053e21e3
    "5256", # libsolidity/analysis/DocStringTagParser.cpp, 614683019bf4423b524da3cb7f442079358ce76c
    "5256", # libsolidity/analysis/DocStringTagParser.cpp, 7d8a4e63d84f548dbb3409f761fb2e92936c9057
    "5256", # libsolidity/analysis/DocStringTagParser.cpp, ad3bc71f270bcec6dd0f5309562496636da4f09f
    "5256", # libsolidity/analysis/DocStringTagParser.cpp, e3e6729f2214cd93a5ddccb54c538914bacf11ff
    "5380", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "5380", # libsolidity/analysis/TypeChecker.cpp, 3e3f9a472f061ed74e91b77259c7b7c3085cb1c1
    "5380", # libsolidity/analysis/TypeChecker.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "5380", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "5380", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "5380", # libsolidity/analysis/TypeChecker.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "5380", # libsolidity/analysis/TypeChecker.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "5380", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "5380", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "5380", # libsolidity/analysis/TypeChecker.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "5380", # libsolidity/analysis/TypeChecker.cpp, a79d7c158837f31319a789ad256b81deec6135e5
    "5380", # libsolidity/analysis/TypeChecker.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "5380", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "5380", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "5380", # libsolidity/analysis/TypeChecker.cpp, d41eaeba5686828b85279057f3a7da8be0f9a8f9
    "5380", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "5380", # libsolidity/analysis/TypeChecker.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "5622", # libsolidity/formal/BMC.cpp, 1da9b3957232132d52c108e6f08ff48b48176192
    "5622", # libsolidity/formal/BMC.cpp, c6d09d996d7be5ca3676a87ef577d2305e68886a
    "5622", # libsolidity/formal/BMC.cpp, eb56b4bfe6fe9996342b27d4fc6a4001725d4446
    "5798", # libyul/AsmParser.cpp, b7edcc51d6eb75ae830215bcbd1f8e4cc812d7e6
    "5798", # libyul/AsmParser.cpp, e5ab68ed71460ad088788ac0bc6d94c16832bcfe
    "5883", # libsolidity/analysis/OverrideChecker.cpp, 1d5350e32f04e991dbfc8fca402cbc8c7930e85d
    "6084", # libsolidity/formal/BMC.cpp, 07427c798c48061c608b1fded06c12bd296fa563
    "6084", # libsolidity/formal/BMC.cpp, 65c2089b43bc6d9b808a01ffb8ccbe53ac362bb8
    "6084", # libsolidity/formal/BMC.cpp, adaf1ff7dfbd4c5aab66e5d38bb6e010bc22c23a
    "6084", # libsolidity/formal/BMC.cpp, bb97363abf4d9b76f8339c2589f59ab82638ce02
    "6084", # libsolidity/formal/BMC.cpp, e8a278eefa7fe04890237d264af0653bd5dca981
    "6151", # libsolidity/analysis/TypeChecker.cpp, 253889cbf17a980c24e0ff97476c85edb84a2496
    "6151", # libsolidity/analysis/TypeChecker.cpp, 36f93921540d12fb4250f699e7bfaf804f1e3363
    "6151", # libsolidity/analysis/TypeChecker.cpp, 5da6bddccbbce7f1ccd0d270ecb9e4d13e58d95e
    "6151", # libsolidity/analysis/TypeChecker.cpp, 61425e354112c061c4d95c4a14486d2ae7a2e03d
    "6151", # libsolidity/analysis/TypeChecker.cpp, ee657f53612b987eaf257d5e5698e80b12defe59
    "6151", # libsolidity/analysis/TypeChecker.cpp, fda352094f0e9f586004dda48daef9788068f523
    "6156", # libsolidity/formal/SMTEncoder.cpp, 78eb37d2596c9416b3fac9881414bf7e9c524de8
    "6156", # libsolidity/formal/SMTEncoder.cpp, ad3caa7ff477e00e5cf41fc54a245095add3ee03
    "6156", # libsolidity/formal/SMTEncoder.cpp, b187d065511a5c35d5a9c094bbc2935186b02ee2
    "6191", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "6191", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "6191", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "6191", # libsolidity/formal/SMTEncoder.cpp, bd0c46abf55cd6d3beae62bd1618ad8463b4e88b
    "6191", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, 241a564fcabb40b829b2ba497dd87d488b83fbb9
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, 5394435bea4e553a86f872b6b2512c50bdef1628
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, 73506e285875c98874cb0fb92168a17822ddb449
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, 9e5a56a6491a250ac455f51c6ccd1941d7f44537
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, aea75d0f5b2163c6b40fe8e1c4206bf8261137b2
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, b5964a932834fe29090e00e7258560f63583864b
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, d31f05fcc062b7242412086c70dc9ccf357be86f
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "6493", # libsolidity/analysis/DeclarationTypeChecker.cpp, f9f3c971c41789557c91df90ddaa9b768af79430
    "6546", # libsolidity/analysis/ReferencesResolver.cpp, 66a8c7d1ab5b744736d1355ba46c9e1d5f090ac8
    "6547", # libsolidity/experimental/analysis/Analysis.cpp, 194b114664c7daebc2ff68af3c573272f5d28913
    "6547", # libsolidity/experimental/analysis/Analysis.cpp, 92f383d8733440688905e2b9201565a8faeaf376
    "6547", # libsolidity/experimental/analysis/Analysis.cpp, ed52376980a93ce60bf9f6b8b42d4a42b00a7a00
    "6635", # liblangutil/ParserBase.cpp, 6965f199fd11cada51c5a97ceb72cc5e14534a17
    "6635", # liblangutil/ParserBase.cpp, 9adbced98e49588bcc29e181f2560c2eadaa22ac
    "6635", # liblangutil/ParserBase.cpp, c43c3c3a3ad68fa0e47edda3df34d717193fde37
    "6635", # liblangutil/ParserBase.cpp, c703b5cd8ceeee3add715100ca04d2ae76c33609
    "6660", # libsolidity/formal/SMTEncoder.cpp, 159d6f9efa639c835a4f28a659e3b91079b77d57
    "6660", # libsolidity/formal/SMTEncoder.cpp, 4e343590635f98f7c1d0973e82f9bafc67e03466
    "6660", # libsolidity/formal/SMTEncoder.cpp, cf7f814a4e08484bf8738c80be839cb1f25de129
    "6672", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "6672", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "6706", # libsolidity/analysis/TypeChecker.cpp, 3e3065ac00bf835cc669120b74b24e00361dc767
    "6706", # libsolidity/analysis/TypeChecker.cpp, 5fedb4eab00ad4829490be6f7fd82a33f7bafeed
    "6706", # libsolidity/analysis/TypeChecker.cpp, 849b16babb372aa9fc4722114c0a46881da9e010
    "6706", # libsolidity/analysis/TypeChecker.cpp, 894478ff8c9c0a6d5ffa091fe66adf560e9c6437
    "6706", # libsolidity/analysis/TypeChecker.cpp, 936ea6f950ffd9b4d4bfaa9cd5ae949be0df58fd
    "6706", # libsolidity/analysis/TypeChecker.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "6706", # libsolidity/analysis/TypeChecker.cpp, b9f2697a3c86f32aada10323f1750bde8bea06bc
    "6715", # libsolidity/analysis/TypeChecker.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "6715", # libsolidity/analysis/TypeChecker.cpp, 3da2cd9e1a6351db2a4e32a60214bb2f5e3ab5ef
    "6715", # libsolidity/analysis/TypeChecker.cpp, 7094e307780b7656f10a95f58874f4cde44b63e7
    "6715", # libsolidity/analysis/TypeChecker.cpp, c5685e70544c86f25d87b93048a8bffa963177c6
    "6756", # libsolidity/formal/SMTEncoder.cpp, 78eb37d2596c9416b3fac9881414bf7e9c524de8
    "6756", # libsolidity/formal/SMTEncoder.cpp, ad3caa7ff477e00e5cf41fc54a245095add3ee03
    "6756", # libsolidity/formal/SMTEncoder.cpp, b187d065511a5c35d5a9c094bbc2935186b02ee2
    "6963", # libsolidity/analysis/TypeChecker.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "6963", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "6963", # libsolidity/analysis/TypeChecker.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "6963", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "6963", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "6963", # libsolidity/analysis/TypeChecker.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "6963", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "6963", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "6963", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "6963", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "6963", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "6983", # libsolidity/analysis/TypeChecker.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "6983", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "6983", # libsolidity/analysis/TypeChecker.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "6983", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "6983", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "6983", # libsolidity/analysis/TypeChecker.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "6983", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "6983", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "6983", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "6983", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "6983", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "7059", # libsolidity/parsing/Parser.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "7059", # libsolidity/parsing/Parser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "7059", # libsolidity/parsing/Parser.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "7059", # libsolidity/parsing/Parser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "7059", # libsolidity/parsing/Parser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "7059", # libsolidity/parsing/Parser.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "7059", # libsolidity/parsing/Parser.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "7059", # libsolidity/parsing/Parser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "7059", # libsolidity/parsing/Parser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "7059", # libsolidity/parsing/Parser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "7059", # libsolidity/parsing/Parser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "7079", # libyul/AsmAnalysis.cpp, 0ac039e4ead3005df78665dc693a8dfc91e69ae6
    "7079", # libyul/AsmAnalysis.cpp, 5ef660b17abaa6f9e3b0dd8a949268806ececcd4
    "7079", # libyul/AsmAnalysis.cpp, 889131321ad5b92fa96ebdf74d9275c3216befcc
    "7079", # libyul/AsmAnalysis.cpp, 8c5fce5b3118334e8671e65453e03b4e0c13ea96
    "7079", # libyul/AsmAnalysis.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "7079", # libyul/AsmAnalysis.cpp, b9b24daa8a0a7bb4482ec79015fa8e43e83f302d
    "7079", # libyul/AsmAnalysis.cpp, d211a45aa4844821e03c38b1abcecb05dafd27fe
    "7079", # libyul/AsmAnalysis.cpp, d67862362a16f03906386d2d2cb4d12e586d6b73
    "7079", # libyul/AsmAnalysis.cpp, f11b0336ad056d22bebd24de902ac633eb9f6d4d
    "7186", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "7186", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "7186", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "7186", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "7186", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "7439", # libsolidity/parsing/Parser.cpp, 10f93fbd8a3007b4e90f9077ac9080740a23c6d8
    "7439", # libsolidity/parsing/Parser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "7439", # libsolidity/parsing/Parser.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "7439", # libsolidity/parsing/Parser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "7439", # libsolidity/parsing/Parser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "7439", # libsolidity/parsing/Parser.cpp, 93c792c696b2929da2b6e2eea31a4c5f60e9188c
    "7439", # libsolidity/parsing/Parser.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "7439", # libsolidity/parsing/Parser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "7439", # libsolidity/parsing/Parser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "7439", # libsolidity/parsing/Parser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "7439", # libsolidity/parsing/Parser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "7484", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "7484", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "7569", # libyul/AsmAnalysis.cpp, 011f8a462d718f3034e72025b1d3d3916faa474d
    "7569", # libyul/AsmAnalysis.cpp, 0b216f57719fbf83d33f3646fa0435327c3d46a4
    "7569", # libyul/AsmAnalysis.cpp, 0e11d468cc9ab5691f7222a7f2f4610497f192b6
    "7569", # libyul/AsmAnalysis.cpp, 1f49edd29d398795660770c4514065d7dfb1bcd4
    "7569", # libyul/AsmAnalysis.cpp, 3e3065ac00bf835cc669120b74b24e00361dc767
    "7569", # libyul/AsmAnalysis.cpp, 65d8b6cf759e5a16087d4b2eaf32bd7d15fe6339
    "7569", # libyul/AsmAnalysis.cpp, 849b16babb372aa9fc4722114c0a46881da9e010
    "7569", # libyul/AsmAnalysis.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "7569", # libyul/AsmAnalysis.cpp, b9f2697a3c86f32aada10323f1750bde8bea06bc
    "7569", # libyul/AsmAnalysis.cpp, c07254f5acc6a7d134b36775dfd8a79acd77bad4
    "7569", # libyul/AsmAnalysis.cpp, c8b9d24eba010f7f876d215a99eb64e7ecd9309d
    "7569", # libyul/AsmAnalysis.cpp, d12db7ec5202b1406bc0e6c4537a4f3def7d7d64
    "7569", # libyul/AsmAnalysis.cpp, f97b376f7e2a8cdf386c12a55bc949d67fabb3e2
    "7645", # libsolidity/formal/SMTEncoder.cpp, 0f3924186ea02f3e335c05940dd8c16d1fb783d1
    "7645", # libsolidity/formal/SMTEncoder.cpp, 66a773aef9af1cf0cf77e0d2ba1bf397995e4526
    "7645", # libsolidity/formal/SMTEncoder.cpp, 7b00f8302fb545e378e346b0149821f983e09a8f
    "7645", # libsolidity/formal/SMTEncoder.cpp, 99add1e4e52818a7ed500fcb96983e7f030a478d
    "7645", # libsolidity/formal/SMTEncoder.cpp, d97b9ba8659fcf58ad67451635b2ca5585bbbc17
    "7645", # libsolidity/formal/SMTEncoder.cpp, e9dcd4f8135179d97eeac57de21f0491c0844474
    "7653", # libsolidity/analysis/TypeChecker.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "7653", # libsolidity/analysis/TypeChecker.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "7653", # libsolidity/analysis/TypeChecker.cpp, 7ac440f35b3b2aa7fb9958c01d63789a5ff53964
    "7653", # libsolidity/analysis/TypeChecker.cpp, 7f15be5549c990f86e38002d20eb0d6abcfc3186
    "7653", # libsolidity/analysis/TypeChecker.cpp, fd9050614a6089168bd4565f4b49c64d04a0ef71
    "7698", # libsolidity/parsing/Parser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "7698", # libsolidity/parsing/Parser.cpp, 308af236156a42b6a05e105ed8ea9c25397554ae
    "7698", # libsolidity/parsing/Parser.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "7698", # libsolidity/parsing/Parser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "7698", # libsolidity/parsing/Parser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "7698", # libsolidity/parsing/Parser.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "7698", # libsolidity/parsing/Parser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "7698", # libsolidity/parsing/Parser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "7698", # libsolidity/parsing/Parser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "7698", # libsolidity/parsing/Parser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "7698", # libsolidity/parsing/Parser.cpp, f73b25bb78e64a57e30ade9c7982d9c2375a3b7b
    "7698", # libsolidity/parsing/Parser.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "7733", # libsolidity/analysis/ImmutableValidator.cpp, 96bb39d1b4569b8eb3f00273cce7741d9f55a662
    "7733", # libsolidity/analysis/ImmutableValidator.cpp, dad2bf64723cc83f0168bae0310714db01983a50
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 1441b97131c7eabe5dd7fa5a60c1375708af010d
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 4222ead28c1bd2d611ac82aa61af5142174a01fe
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 71cb7551f46051244b9a18628e213b863ff5f47a
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 8155ad2187c1e88eaebcdcc17f7eabfe0bc6e644
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, af0cd4ab98094e9b765eda86e499f8dd70c7646b
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, cb5bfc7436ca11bdfa2f0543a3611079e3f4cbee
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, d7899a31afd8e1132ce362c522e8a47c17fd3832
    "7816", # libsolidity/analysis/DocStringAnalyser.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "7816", # libsolidity/analysis/DocStringTagParser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "7885", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "7885", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "7885", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "7885", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "7885", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "7989", # libsolidity/formal/SMTEncoder.cpp, 2037b7d6b8dd66ffc30f28cd3abaf77711a56896
    "7989", # libsolidity/formal/SMTEncoder.cpp, 4bdec8107cbedeaed3cfca0845c6b324b42b75b2
    "7989", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "7989", # libsolidity/formal/SMTEncoder.cpp, 57e1b2cb928e82a7e853ec363690d510b1f554b9
    "7989", # libsolidity/formal/SMTEncoder.cpp, 9115100f2ac5521c82fcbf5e5656bb706c61e04b
    "7989", # libsolidity/formal/SMTEncoder.cpp, df8c6d94e30b8c66785e8c77c47a3b080270d194
    "8182", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "8182", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "8182", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "8182", # libsolidity/formal/SMTEncoder.cpp, bd0c46abf55cd6d3beae62bd1618ad8463b4e88b
    "8182", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "8195", # libsolidity/formal/SMTEncoder.cpp, 095d33714086880ded0f2ce2c7a8e4493e379613
    "8195", # libsolidity/formal/SMTEncoder.cpp, 159d6f9efa639c835a4f28a659e3b91079b77d57
    "8195", # libsolidity/formal/SMTEncoder.cpp, cf7f814a4e08484bf8738c80be839cb1f25de129
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, 6fd5ea01d1c943b7b40afbc72fcb60be3bb2a78a
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, 78a097a012c8abd42b29b4dd2d38bf16a5b7cdc1
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, 7d0ecd940679e2973a602bcc4421c05278e2be2d
    "8261", # libsolidity/analysis/NameAndTypeResolver.cpp, e75e3fc2e321cd00cabfe2cd0ab4b191eefd76ce
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 1441b97131c7eabe5dd7fa5a60c1375708af010d
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 4222ead28c1bd2d611ac82aa61af5142174a01fe
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 71cb7551f46051244b9a18628e213b863ff5f47a
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 8155ad2187c1e88eaebcdcc17f7eabfe0bc6e644
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 982a269b2bac114d74f18b09e17d7112a85dba4f
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, af0cd4ab98094e9b765eda86e499f8dd70c7646b
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, cb5bfc7436ca11bdfa2f0543a3611079e3f4cbee
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, d7899a31afd8e1132ce362c522e8a47c17fd3832
    "8532", # libsolidity/analysis/DocStringAnalyser.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "8532", # libsolidity/analysis/DocStringTagParser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "8532", # libsolidity/analysis/ReferencesResolver.cpp, 66a8c7d1ab5b744736d1355ba46c9e1d5f090ac8
    "9011", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "9011", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "9011", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "9011", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "9011", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "9054", # libsolidity/analysis/TypeChecker.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "9054", # libsolidity/analysis/TypeChecker.cpp, 41e1e34211c1255e789b186f7e762f9e07d27deb
    "9054", # libsolidity/analysis/TypeChecker.cpp, 64b6524bdb68f4c7dcbf7bfdc73578da24cb9a79
    "9054", # libsolidity/analysis/TypeChecker.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "9054", # libsolidity/analysis/TypeChecker.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "9054", # libsolidity/analysis/TypeChecker.cpp, 8eee3ed3a24436d7076fcf636fcfa95fed57a535
    "9054", # libsolidity/analysis/TypeChecker.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "9054", # libsolidity/analysis/TypeChecker.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "9054", # libsolidity/analysis/TypeChecker.cpp, 9ef050af9a669433788e130a0fa8701b229c576a
    "9054", # libsolidity/analysis/TypeChecker.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "9054", # libsolidity/analysis/TypeChecker.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "9054", # libsolidity/analysis/TypeChecker.cpp, da36400576304bc6daa924d40684b6655914e4a5
    "9054", # libsolidity/analysis/TypeChecker.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "9054", # libsolidity/analysis/TypeChecker.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "9056", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "9056", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "9056", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "9056", # libsolidity/formal/SMTEncoder.cpp, bd0c46abf55cd6d3beae62bd1618ad8463b4e88b
    "9056", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "9085", # libsolidity/analysis/TypeChecker.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "9085", # libsolidity/analysis/TypeChecker.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "9085", # libsolidity/analysis/TypeChecker.cpp, c812d928fd5adfdadc6a4ccbf03e5af916598a11
    "9085", # libsolidity/analysis/TypeChecker.cpp, f766700000e1c50f400581fc647f71daef2bb588
    "9118", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "9118", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "9118", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "9118", # libsolidity/formal/SMTEncoder.cpp, e61b731647b88fe97ee648c4035ecb0fe210eaf0
    "9118", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "9149", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "9149", # libsolidity/formal/SMTEncoder.cpp, 763282343f9e0d169cddfa3df10bead69814ee87
    "9149", # libsolidity/formal/SMTEncoder.cpp, 79f550dba94d5831be264745012cf0433556d8fb
    "9149", # libsolidity/formal/SMTEncoder.cpp, 858b4507e2c5e07a0f72108538edc8ec52c935c1
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 50c3daf693189096296d5527f626823cfdbef50b
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 9be5ed1220ebf9ae26e08a5f4e99176d64e30b9a
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, cf189a32859fae2b50315dbfddc5535c7afc0c48
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, f94516390973a94be9ba3997528c5923a11eb964
    "9155", # libsolidity/analysis/ReferencesResolver.cpp, fc2e9ec2ff4ca397f0aa743cc44b40352894fec2
    "9222", # libsolidity/parsing/DocStringParser.cpp, 1ec1166a27a002090c0402f05165a6da73e2af76
    "9222", # libsolidity/parsing/DocStringParser.cpp, 2d64f53a39f4a32f3560e0e8cb2c5d0908fc278f
    "9222", # libsolidity/parsing/DocStringParser.cpp, 3d96e2b11a45c22f78336e74c9f6f9c89097efed
    "9222", # libsolidity/parsing/DocStringParser.cpp, 46bcac58eb1010b61a9c8ef36c7fa49679db8622
    "9222", # libsolidity/parsing/DocStringParser.cpp, 5ef660b17abaa6f9e3b0dd8a949268806ececcd4
    "9222", # libsolidity/parsing/DocStringParser.cpp, ab68406006edf46a0a897eaedfa159b0ff021508
    "9222", # libsolidity/parsing/DocStringParser.cpp, acd42a08c1b1fe0f69dbcd9c97ac75cc0b1b352b
    "9222", # libsolidity/parsing/DocStringParser.cpp, b0bc74700041688011806e872a008252a4e05e87
    "9222", # libsolidity/parsing/DocStringParser.cpp, d67862362a16f03906386d2d2cb4d12e586d6b73
    "9239", # libsolidity/analysis/TypeChecker.cpp, da36400576304bc6daa924d40684b6655914e4a5
    "9390", # libsolidity/analysis/TypeChecker.cpp, 069ac9c9a9962fd8524a1e3b41d51c4837efaca8
    "9390", # libsolidity/analysis/TypeChecker.cpp, 596e8dd9b661e5c86db259571811efbf2fbe9d2a
    "9390", # libsolidity/analysis/TypeChecker.cpp, 7ac440f35b3b2aa7fb9958c01d63789a5ff53964
    "9390", # libsolidity/analysis/TypeChecker.cpp, 7f15be5549c990f86e38002d20eb0d6abcfc3186
    "9390", # libsolidity/analysis/TypeChecker.cpp, fd9050614a6089168bd4565f4b49c64d04a0ef71
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, 0b45168bcbf5ed5874668f21a3c3d1476cab5620
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, 241a564fcabb40b829b2ba497dd87d488b83fbb9
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, d31f05fcc062b7242412086c70dc9ccf357be86f
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, dec0f86b832662e546994dab0680064a589caec9
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, f079efe28c446516b1702cc134622ccdf307b0f6
    "9440", # libsolidity/analysis/DocStringTagParser.cpp, f4a555bedca52f4c1d4288375ec1e3abcb3d1d6d
    "9547", # libyul/AsmAnalysis.cpp, 0d0f2771654b14ee0e8d317a5eb22dbff8eab332
    "9547", # libyul/AsmAnalysis.cpp, 168850b48d59a338bfe160ebcfb3ed13f8a0c087
    "9547", # libyul/AsmAnalysis.cpp, 664ee2327d24ffb89f6632a2aff12fa28743b839
    "9551", # libsolidity/formal/SMTEncoder.cpp, 088b694f0ba1d3f08fb1e4acbd962b31210ad4ae
    "9551", # libsolidity/formal/SMTEncoder.cpp, 27e44b85e34447a882eccfd3704cb41210a8d08a
    "9551", # libsolidity/formal/SMTEncoder.cpp, 3862ceb5287b31384a7be766353913cada779c01
    "9551", # libsolidity/formal/SMTEncoder.cpp, d56a7bb89e38149f83e21bd381f664d5a68b65e1
    "9551", # libsolidity/formal/SMTEncoder.cpp, fa561dbd0e839ce5e198059a0eff139e5860ea89
    "9595", # libyul/AsmAnalysis.cpp, 011f8a462d718f3034e72025b1d3d3916faa474d
    "9595", # libyul/AsmAnalysis.cpp, 0b216f57719fbf83d33f3646fa0435327c3d46a4
    "9595", # libyul/AsmAnalysis.cpp, 0e11d468cc9ab5691f7222a7f2f4610497f192b6
    "9595", # libyul/AsmAnalysis.cpp, 1f49edd29d398795660770c4514065d7dfb1bcd4
    "9595", # libyul/AsmAnalysis.cpp, 3e3065ac00bf835cc669120b74b24e00361dc767
    "9595", # libyul/AsmAnalysis.cpp, 65d8b6cf759e5a16087d4b2eaf32bd7d15fe6339
    "9595", # libyul/AsmAnalysis.cpp, 849b16babb372aa9fc4722114c0a46881da9e010
    "9595", # libyul/AsmAnalysis.cpp, b4c6fdb1ed4c6627a04a2181040c06f9982d852e
    "9595", # libyul/AsmAnalysis.cpp, b9f2697a3c86f32aada10323f1750bde8bea06bc
    "9595", # libyul/AsmAnalysis.cpp, c07254f5acc6a7d134b36775dfd8a79acd77bad4
    "9595", # libyul/AsmAnalysis.cpp, c8b9d24eba010f7f876d215a99eb64e7ecd9309d
    "9595", # libyul/AsmAnalysis.cpp, d12db7ec5202b1406bc0e6c4537a4f3def7d7d64
    "9595", # libyul/AsmAnalysis.cpp, f97b376f7e2a8cdf386c12a55bc949d67fabb3e2
    "9599", # libsolidity/formal/SMTEncoder.cpp, 2fb8beb71434dd01244f913edcc127331ee5876b
    "9599", # libsolidity/formal/SMTEncoder.cpp, 51b20bc0872bb9049e205d5547023cb06d1df9db
    "9599", # libsolidity/formal/SMTEncoder.cpp, 72f8a753a94fc2845b1bd6db49cbfad8cd7c09c3
    "9599", # libsolidity/formal/SMTEncoder.cpp, bd0c46abf55cd6d3beae62bd1618ad8463b4e88b
    "9599", # libsolidity/formal/SMTEncoder.cpp, f964966090f7e3571e20144fd4aa0b6391aea26e
    "9609", # libsolidity/interface/CompilerStack.cpp, 0e8e4eacd59194f66571e136e635e1921af392e5
    "9609", # libsolidity/interface/CompilerStack.cpp, a695089fecd2b3168648fb14373aa76c736a13bb
    "9817", # libsolidity/experimental/analysis/TypeInference.cpp, 1906cf13c1308ed88f8ec102489d6d0d933f8090
    "9817", # libsolidity/experimental/analysis/TypeInference.cpp, fb99132474c177fc861305feeafd43b9cbb93b66
    "9843", # libsolidity/analysis/DocStringAnalyser.cpp, cdb7aa5d13ffd6af1e8df394864266c28720d193
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, 2fece0724ab1284a97d7b7a078253e388e5bb9d3
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, 6bb6783d3939ace2b21ce27bf2765b2875097f37
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, 845c1ae91f4681b714c64636af908751a5ea340d
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, 8b7567f963e00ef15fd5ae97c310064658612ae9
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, 9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, ae41cc4da5bf1ab0e15ee7fb43e03bb87abb32ac
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, ba4e05c62c2bc3de8b924448b622ca35a0636370
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, d08d78cb560f93b2388d187dd9f0348210337896
    "9843", # libsolidity/analysis/DocStringTagParser.cpp, ef49906f94987b43cfc4999358b538adb1d1b551
}


def read_file(file_name):
    content = None
    _, tail = path.split(file_name)
    is_latin = tail == "invalid_utf8_sequence.sol"
    try:
        with open(file_name, "r", encoding="latin-1" if is_latin else ENCODING) as f:
            content = f.read()
    finally:
        if content is None:
            print(f"Error reading: {file_name}")
    return content


def write_file(file_name, content):
    with open(file_name, "w", encoding=ENCODING) as f:
        f.write(content)


def in_comment(source, pos):
    slash_slash_pos = source.rfind("//", 0, pos)
    lf_pos = source.rfind("\n", 0, pos)
    if slash_slash_pos > lf_pos:
        return True
    slash_star_pos = source.rfind("/*", 0, pos)
    star_slash_pos = source.rfind("*/", 0, pos)
    return slash_star_pos > star_slash_pos


def find_ids_in_source_file(file_name, id_to_file_names):
    source = read_file(file_name)
    for m in re.finditer(SOURCE_FILE_PATTERN, source):
        if in_comment(source, m.start()):
            continue
        underscore_pos = m.group(0).index("_")
        error_id = m.group(0)[0:underscore_pos]
        if error_id in id_to_file_names:
            id_to_file_names[error_id].append(file_name)
        else:
            id_to_file_names[error_id] = [file_name]


def find_ids_in_source_files(file_names):
    """Returns a dictionary with list of source files for every appearance of every id"""

    id_to_file_names = {}
    for file_name in file_names:
        find_ids_in_source_file(file_name, id_to_file_names)
    return id_to_file_names


def get_next_id(available_ids):
    assert len(available_ids) > 0, "Out of IDs"
    next_id = random.choice(list(available_ids))
    available_ids.remove(next_id)
    return next_id


def fix_ids_in_source_file(file_name, id_to_count, available_ids):
    source = read_file(file_name)

    k = 0
    destination = []
    for m in re.finditer(SOURCE_FILE_PATTERN, source):
        destination.extend(source[k:m.start()])

        underscore_pos = m.group(0).index("_")
        error_id = m.group(0)[0:underscore_pos]

        # incorrect id or id has a duplicate somewhere
        if not in_comment(source, m.start()) and (len(error_id) != 4 or error_id[0] == "0" or id_to_count[error_id] > 1):
            assert error_id in id_to_count
            new_id = get_next_id(available_ids)
            assert new_id not in id_to_count
            id_to_count[error_id] -= 1
        else:
            new_id = error_id

        destination.extend(new_id + "_error")
        k = m.end()

    destination.extend(source[k:])

    destination = ''.join(destination)
    if source != destination:
        write_file(file_name, destination)
        print(f"Fixed file: {file_name}")


def fix_ids_in_source_files(file_names, id_to_count, available_ids):
    """
    Fixes ids in given source files;
    id_to_count contains number of appearances of every id in sources
    """

    for file_name in file_names:
        fix_ids_in_source_file(file_name, id_to_count, available_ids)


def find_files(top_dir, sub_dirs, extensions):
    """Builds a list of files with given extensions in specified subdirectories"""

    source_file_names = []
    for directory in sub_dirs:
        for root, _, file_names in os.walk(os.path.join(top_dir, directory), onerror=lambda e: sys.exit(f"Walk error: {e}")):
            for file_name in file_names:
                _, ext = path.splitext(file_name)
                if ext in extensions:
                    source_file_names.append(path.join(root, file_name))

    return source_file_names


def find_source_files(dir):
    return find_files(
        dir,
        ["libevmasm", "liblangutil", "libsolc", "libsolidity", "libsolutil", "libyul", "solc"],
        [".h", ".cpp"]
    )


def find_ids_in_test_file(file_name):
    source = read_file(file_name)
    pattern = r"^// (.*Error|Warning|Info) \d\d\d\d:"
    return {m.group(0)[-5:-1] for m in re.finditer(pattern, source, flags=re.MULTILINE)}


def find_ids_in_test_files(file_names):
    """Returns a set containing all ids in tests"""

    ids = set()
    for file_name in file_names:
        ids |= find_ids_in_test_file(file_name)
    return ids


def find_ids_in_cmdline_test_err(file_name):
    source = read_file(file_name)
    pattern = r' \(\d\d\d\d\):'
    return {m.group(0)[-6:-2] for m in re.finditer(pattern, source, flags=re.MULTILINE)}


def print_ids(ids):
    for k, error_id in enumerate(sorted(ids)):
        if k % 10 > 0:
            print(" ", end="")
        elif k > 0:
            print()
        print(error_id, end="")


def print_ids_per_file(ids, id_to_file_names, top_dir):
    file_name_to_ids = {}
    for error_id in ids:
        for file_name in id_to_file_names[error_id]:
            relpath = path.relpath(file_name, top_dir)
            if relpath not in file_name_to_ids:
                file_name_to_ids[relpath] = []
            file_name_to_ids[relpath].append(error_id)

    for file_name in sorted(file_name_to_ids):
        print(file_name)
        for error_id in sorted(file_name_to_ids[file_name]):
            print(f" {error_id}", end="")
        print()


def examine_id_coverage(top_dir, source_id_to_file_names, new_ids_only=False):
    test_sub_dirs = [
        path.join("test", "libsolidity", "natspecJSON"),
        path.join("test", "libsolidity", "smtCheckerTests"),
        path.join("test", "libsolidity", "syntaxTests"),
        path.join("test", "libyul", "yulSyntaxTests")
    ]
    test_file_names = find_files(
        top_dir,
        test_sub_dirs,
        [".sol", ".yul"]
    )
    source_ids = source_id_to_file_names.keys()
    test_ids = find_ids_in_test_files(test_file_names)

    # special case, we are interested in warnings which are ignored by regular tests:
    # Warning (1878): SPDX license identifier not provided in source file. ....
    # Warning (3420): Source file does not specify required compiler version!
    test_ids |= find_ids_in_cmdline_test_err(path.join(top_dir, "test", "cmdlineTests", "error_codes", "err"))

    # white list of ids which are not covered by tests
    white_ids = {
        "9804", # Tested in test/libyul/ObjectParser.cpp.
        "1544",
        "1749",
        "2674",
        "6367",
        "8387",
        "3805", # "This is a pre-release compiler version, please do not use it in production."
                # The warning may or may not exist in a compiler build.
        "4591", # "There are more than 256 warnings. Ignoring the rest."
                # Due to 3805, the warning lists look different for different compiler builds.
        "1920", # Unimplemented feature error from YulStack (currently there are no UnimplementedFeatureErrors thrown by libyul)
        "7053", # Unimplemented feature error (parsing stage), currently has no tests
        "2339", # SMTChecker, covered by CL tests
        "6240", # SMTChecker, covered by CL tests
        "2788", # SMTChecker: BMC: verification condition(s) could not be proved
        "1733", # AsmAnalysis: expecting bool expression (everything is implicitly bool without types in Yul)
        "9547", # AsmAnalysis: assigning incompatible types in Yul (whitelisted as there are currently no types)
        "5026", # ContractLevelChecker: too difficult to exceed transient storage max size due to only value types supported.
    }
    assert len(test_ids & white_ids) == 0, "The sets are not supposed to intersect"
    test_ids |= white_ids

    test_only_ids = test_ids - source_ids
    source_only_ids = source_ids - test_ids

    if not new_ids_only:
        print(f"IDs in source files: {len(source_ids)}")
        print(f"IDs in test files  : {len(test_ids)} ({len(test_ids) - len(source_ids)})")
        print()

        if len(test_only_ids) != 0:
            print("Error. The following error codes found in tests, but not in sources:")
            print_ids(test_only_ids)
            return False

        if len(source_only_ids) != 0:
            print("The following error codes found in sources, but not in tests:")
            print_ids_per_file(source_only_ids, source_id_to_file_names, top_dir)
            print("\n\nPlease make sure to add appropriate tests.")
            return False

    old_source_only_ids = {
        "1218",
        "1584",
        "1823",
        "1988",
        "2066",
        "2833",
        "3356",
        "3893",
        "3996",
        "4010",
        "4458",
        "4802",
        "4902",
        "5272",
        "5798",
        "5840",
        "7128",
        "7400",
        "7589",
        "7593",
        "7649",
        "7710",
        "8065",
        "8084",
        "8140",
        "8158",
        "8312",
        "8592",
        "9134",
        "9609",
    }

    # TODO Cover these with tests and remove from this list as the development of experimental
    # TODO Solidity progresses. The aim should be to completely get rid of `experimental_source_only_ids`.
    experimental_source_only_ids = {
        "1017",
        "1439",
        "1723",
        "1741",
        "1801",
        "1807",
        "2015",
        "2345",
        "2399",
        "2599",
        "2655",
        "2934",
        "3101",
        "3111",
        "3195",
        "3520",
        "3573",
        "3654",
        "4316",
        "4337",
        "4496",
        "4504",
        "4686",
        "4767",
        "4873",
        "4955",
        "5044",
        "5094",
        "5096",
        "5104",
        "5195",
        "5262",
        "5348",
        "5360",
        "5387",
        "5577",
        "5714",
        "5731",
        "5755",
        "5904",
        "6175",
        "6387",
        "6388",
        "6460",
        "6620",
        "6739",
        "6948",
        "7341",
        "7428",
        "7531",
        "8379",
        "8809",
        "8953",
        "9159",
        "9173",
        "9282",
        "9603",
        "9658",
        "9988",
    }

    new_source_only_ids = source_only_ids - old_source_only_ids - experimental_source_only_ids
    if len(new_source_only_ids) != 0:
        print("The following new error code(s), not covered by tests, found:")
        print_ids(new_source_only_ids)
        print(
            "\nYou can:\n"
            "- create appropriate test(s);\n"
            "- add the error code(s) to old_source_only_ids in error_codes.py\n"
            "  (to silence the checking script, with a promise to add a test later);\n"
            "- add the error code(s) to white_ids in error_codes.py\n"
            "  (for rare cases when the error is not supposed to be tested)"
        )
        return False

    return True

def find_ids_in_branch(branch_commit):
    """Returns a set of error codes present in the given branch/commit"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a temporary worktree to examine the target branch
        subprocess.run(['git', 'worktree', 'add', tmp_dir, branch_commit], check=True)
        
        source_file_names = find_source_files(tmp_dir)
        ids = find_ids_in_source_files(source_file_names).keys()
        
        # Clean up the worktree
        subprocess.run(['git', 'worktree', 'remove', '--force', tmp_dir], check=True)
        
        return set(ids)


def check_removed_error_codes_between_branches():
    """
    Checks if any error codes were removed between target branch and current branch
    but not added to REMOVED_IDS. Returns True if all removed codes are properly tracked.
    """

    # Get the merge base (common ancestor) with the target branch
    # If PR_TARGET_BRANCH env var is set (job chk_errorcodes from CI), use that, otherwise use origin/develop
    target_branch = os.getenv('PR_TARGET_BRANCH', PR_DEFAULT_BRANCH)
    try:
        merge_base = subprocess.check_output(
            ['git', 'merge-base', target_branch, 'HEAD'],
            universal_newlines=True
        ).strip()
    except subprocess.CalledProcessError:
        print(f"Error: Could not find merge base with {target_branch}")
        return False

    # Get error codes from target branch
    try:
        target_ids = find_ids_in_branch(merge_base)
    except subprocess.CalledProcessError as e:
        print(f"Error accessing target branch: {e}")
        return False

    # Get error codes from current branch
    source_file_names = find_source_files(".")
    current_ids = set(find_ids_in_source_files(source_file_names).keys())

    # Find removed error codes (present in target but not in current and not in REMOVED_IDS)
    removed_ids = target_ids - current_ids - REMOVED_IDS

    if len(removed_ids) > 0:
        print(f"Error: The following error codes were removed since {target_branch} but not added to REMOVED_IDS:")
        print_ids(removed_ids)
        print("\nPlease add these codes to the REMOVED_IDS set in scripts/error_codes.py")
        return False

    return True


def main(argv):
    check = False
    fix = False
    no_confirm = False
    examine_coverage = False
    next_id = False
    check_removed = False
    opts, _args = getopt.getopt(argv, "", ["check", "fix", "no-confirm", "examine-coverage", "next", "check-removed"])

    for opt, _arg in opts:
        if opt == "--check":
            check = True
        elif opt == "--fix":
            fix = True
        elif opt == "--no-confirm":
            no_confirm = True
        elif opt == "--examine-coverage":
            examine_coverage = True
        elif opt == "--next":
            next_id = True
        elif opt == "--check-removed":
            check_removed = True

    if [check, fix, examine_coverage, next_id, check_removed].count(True) != 1:
        print("usage: python error_codes.py --check | --fix [--no-confirm] | --examine-coverage | --next | --check-removed")
        sys.exit(1)

    if check_removed:
        res = 0 if check_removed_error_codes_between_branches() else 1
        sys.exit(res)

    cwd = os.getcwd()

    source_file_names = find_source_files(cwd)
    source_id_to_file_names = find_ids_in_source_files(source_file_names)

    ok = True
    for error_id in sorted(source_id_to_file_names):
        if len(error_id) != 4:
            print(f"ID {error_id} length != 4")
            ok = False
        if error_id[0] == "0":
            print(f"ID {error_id} starts with zero")
            ok = False
        if len(source_id_to_file_names[error_id]) > 1:
            print(f"ID {error_id} appears {len(source_id_to_file_names[error_id])} times")
            ok = False

    if examine_coverage:
        if not ok:
            print("Incorrect IDs have to be fixed before applying --examine-coverage")
            sys.exit(1)
        res = 0 if examine_id_coverage(cwd, source_id_to_file_names) else 1
        sys.exit(res)

    ok &= examine_id_coverage(cwd, source_id_to_file_names, new_ids_only=True)

    random.seed()

    available_ids = {str(error_id) for error_id in range(1000, 10000)} - source_id_to_file_names.keys() - REMOVED_IDS

    if next_id:
        if not ok:
            print("Incorrect IDs have to be fixed before applying --next")
            sys.exit(1)
        next_id = get_next_id(available_ids)
        print(f"Next ID: {next_id}")
        sys.exit(0)

    if ok:
        print("No incorrect IDs found")
        sys.exit(0)

    if check:
        sys.exit(1)

    assert fix, "Unexpected state, should not come here without --fix"

    if not no_confirm:
        answer = input(
            "\nDo you want to fix incorrect IDs?\n"
            "Please commit current changes first, and review the results when the script finishes.\n"
            "[Y/N]? "
        )
        while len(answer) == 0 or answer not in "YNyn":
            answer = input("[Y/N]? ")
        if answer not in "yY":
            sys.exit(1)

    # number of appearances for every id
    source_id_to_count = { error_id: len(file_names) for error_id, file_names in source_id_to_file_names.items() }

    fix_ids_in_source_files(source_file_names, source_id_to_count, available_ids)
    print("Fixing completed")
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
