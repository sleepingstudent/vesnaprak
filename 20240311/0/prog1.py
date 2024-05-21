import cmd
from calendar import TextCalendar


class c1(cmd.Cmd):
    prompt = ":->"
    Months = {m.name: m.value for m in calendat.Month}

    def do_prmonth(self, args):
        args = args.split()
        if len(args) == 2:
            month = self.Months[args[1]]
            TextCalendar().prmonth(int(args[0]), month)
    
    def do_pryear(self, args):
        args = args.split()
        TextCalendar().pryear(int(args[0]), int(args[1]))
    
    def complete prmonth(self, text, line, bidx, eidx):
        if len(line) >= 2:
            return [m for m in self.Months if m.startswith(text)]

if __name__ == "__main__":
    c1().cmdloop()
