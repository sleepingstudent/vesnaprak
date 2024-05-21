import cmd


class Echoer(cmd.Cmd):
    """Dumb echo command REPL"""
    prompt = ":->"

    def do_echo(self, args):
        print(args+' Alina, s 8 marta <3')

    def do_EOF(self, args):
        return True


if __name__ == '__main__':
    Echoer().cmdloop()
