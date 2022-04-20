
import pendulum
# Core imports
import duckling #import (load_time_zones, parse_ref_time,
                    #   parse_lang, default_locale_lang, parse_locale,
                    #   parse_dimensions, parse, Context)

class DateHelper:
        
    def parse_text(self, x):
        # Load reference time for time parsing
        time_zones = duckling.load_time_zones("/usr/share/zoneinfo")
        bog_now = pendulum.now('Europe/Madrid').replace(microsecond=0)
        ref_time = duckling.parse_ref_time(time_zones, 'Europe/Madrid', bog_now.int_timestamp)

        # Load language/locale information
        lang_es = duckling.parse_lang('EN')
        default_locale = duckling.default_locale_lang(lang_es)
        locale = duckling.parse_locale('EN', default_locale)

        # Create parsing context with time and language information
        context = duckling.Context(ref_time, locale)

        # Define dimensions to look-up for
        valid_dimensions = ["amount-of-money", "credit-card-number", "distance",
                            "duration", "email", "number", "ordinal",
                            "phone-number", "quantity", "temperature",
                            "time", "time-grain", "url", "volume"]

        # Parse dimensions to use
        output_dims = duckling.parse_dimensions(valid_dimensions)
        result = duckling.parse(x, context, output_dims, False)
        return result
        
