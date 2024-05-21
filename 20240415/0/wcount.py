import gettext


translation = gettext.translation("wcount", "po", fallback=False)
_, ngettext = translation.gettext, translation.ngettext
while a:=input():
    n = len(a.split())
    print(ngettext("Entered {} word", "Entered {} words", n).format(n))