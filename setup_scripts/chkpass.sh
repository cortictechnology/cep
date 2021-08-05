#!/usr/bin/env bash

xcorrect=0 xwrong=1 enouser=2 enodata=3 esyntax=4 ehash=5  IFS=$
die() {
    printf '%s: %s\n' "$0" "$2" >&2
    exit $1
}
report() {
    if (($1 == xcorrect))
        then echo 'Correct password.'
        else echo 'Wrong password.'
    fi
    exit $1
}

(($# == 1)) || die $esyntax "Usage: $(basename "$0") <username>"
case "$(getent passwd "$1" | awk -F: '{print $2}')" in
    x)  ;;
    '') die $enouser "error: user '$1' not found";;
    *)  die $enodata "error: $1's password appears unshadowed!";;
esac

if [ -t 0 ]; then
    IFS= read -rsp "[$(basename "$0")] password for $1: " pass
    printf '\n'
else
    IFS= read -r pass
fi

set -f; ent=($(getent shadow "$1" | awk -F: '{print $2}')); set +f
case "${ent[1]}" in
    1) hashtype=md5;;   5) hashtype=sha-256;;   6) hashtype=sha-512;;
    '') case "${ent[0]}" in
            \*|!)   report $xwrong;;
            '')     die $enodata "error: no shadow entry (are you root?)";;
            *)      die $enodata 'error: failure parsing shadow entry';;
        esac;;
    *)  die $ehash "error: password hash type is unsupported";;
esac

if [[ "${ent[*]}" = "$(mkpasswd -sm $hashtype -S "${ent[2]}" <<<"$pass")" ]]
    then report $xcorrect
    else report $xwrong
fi
