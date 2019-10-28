;; HTML-based remote control
;; Copyright (C) 2019 Ingo Ruhnke <grumbel@gmail.com>
;;
;; This program is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.
;;
;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.
;;
;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.

(use-modules (guix packages)
             (guix gexp)
             (guix download)
             (guix git-download)
             (guix build-system python)
             (guix licenses)
             (gnu packages freedesktop)
             (gnu packages python))

(define %source-dir (dirname (current-filename)))

(define-public python-yattag
  (package
    (name "python-yattag")
    (version "1.12.2")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "yattag" version))
       (sha256
        (base32
         "1g0zhf09vs8cq0l5lx10dnqpimvg5mzh9k0z12n6nnfsw11cila7"))))
    (build-system python-build-system)
    (home-page "https://www.yattag.org/")
    (synopsis "Library for generating HTML or XML in a pythonic way")
    (description "With Yattag,
@itemize
@item you don't have to worry about closing HTML tags
@item your HTML templates are Python code. Not a weird template language. Just Python.
@item you can easily render HTML forms, with defaults values and error messages.
@end itemize
It's actually easier and more readable to generate dynamic HTML with
Yattag than to write static HTML.")
    (license lgpl3+)))

(define-public htmlremote
  (package
    (name "htmlremote")
    (version "0.1.0")
    (source
     (local-file %source-dir
                 #:recursive? #t
                 #:select? (git-predicate %source-dir)))
    (build-system python-build-system)
    (inputs
     `(("python" ,python)
       ("python-pyxdg" ,python-pyxdg)
       ("python-yattag" ,python-yattag)))
    (home-page "https://gitlab.com/grumbel/htmlremote")
    (synopsis "Remote control your computer via the web")
    (description "htmlremote is a simple Python based webserver that
provides remote access to a Linux machine via the web.")
    (license gpl3+)))

htmlremote

;; EOF ;;
