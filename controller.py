import wrapper

def company_search(name):
    check = wrapper.Markit()
    data = check.company_search(name)
    if(data is not None):
        return data
    else:
        return (False)


def get_quote(symbol):
	quote = wrapper.Markit()
	data =  quote.get_quote(symbol)
	if(data is not None):
		return data
	else:
		return (False)

#AlphaVantage


def av_get_quote(symbol):
	quote = wrapper.Alpha()
	data =  quote.av_get_quote(symbol)
	if(data is not None):
		return data
	else:
		return (False)




