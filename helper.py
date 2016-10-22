import os
import jinja2


class Jinja_helper():
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                   autoescape=True)

    @classmethod
    def render_str(cls, template, **params):
        t = cls.jinja_env.get_template(template)
        return t.render(params)
