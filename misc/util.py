import click


def confirm(text, fg='blue', **kwargs):
    """
    Confirm prompt
    :param text: prompt text
    :param fg: foreground color
    :param kwargs: other arguments
    :return: confirmation result
    """
    return click.confirm(click.style('> {}'.format(text), fg=fg, bold=True),
                         **kwargs)


def confirmation(text, **confirm_args):
    """
    Decorator for confirmation (Yes for running function, No for not)
    :param text: prompt text
    :param confirm_args: arguments for confirmation
    :return: confirmation result
    """
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            if confirm(text, **confirm_args):
                func(*args, **kwargs)

        return wrapper

    return real_decorator


def prompt(text, **kwargs):
    """
    Popup a prompt
    :param text: prompt text
    :param kwargs: other arguments
    :return: user input
    """
    return click.prompt(click.style('> {}'.format(text), fg='blue', bold=True),
                        **kwargs)


def choice(text, choices, **kwargs):
    """
    Popup a choice prompt
    :param text: prompt text
    :param choices: choices for user to choose
    :param kwargs: other arguments
    :return: user choice
    """
    return click.prompt(click.style('> {}'.format(text), fg='blue', bold=True),
                        type=click.Choice(choices),
                        **kwargs)


def status(text):
    """
    Print running status
    :param text: status text
    """
    click.secho('{}'.format(text), fg='blue', bold=True)


def info(text):
    """
    Print running info
    :param text: status text
    """
    click.secho('{}'.format(text), fg='green', bold=True)


def warning(text):
    """
    Print warning message
    :param text: warning message
    """
    click.secho('{}'.format(text), fg='yellow', bold=True)


def error(text):
    """
    Print error message
    :param text: error message
    """
    click.secho('{}'.format(text), fg='red', bold=True)
