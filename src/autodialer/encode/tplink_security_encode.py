"""Reverse engineered from the TPLINK router's javascript code
Raw code:

    this.orgAuthPwd = function(a) {
        return this.securityEncode(a, "RDpbLfCPsJZ7fiv", "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW")
    }
    ;
    this.securityEncode = function(a, c, b) {
        var d = "", e, f, g, h, k = 187, l = 187;
        f = a.length;
        g = c.length;
        h = b.length;
        e = f > g ? f : g;
        for (var m = 0; m < e; m++)
            l = k = 187,
            m >= f ? l = c.charCodeAt(m) : m >= g ? k = a.charCodeAt(m) : (k = a.charCodeAt(m),
            l = c.charCodeAt(m)),
            d += b.charAt((k ^ l) % h);
        return d
    }
    ;
"""
def tplink_security_encode(password):
    key = "RDpbLfCPsJZ7fiv"
    dictionary = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"
    d = ""
    f = len(password)
    g = len(key)
    h = len(dictionary)
    
    # Use the length of the longer string
    e = max(f, g)
    
    for m in range(e):
        # Default fallback is 187 (the 'k' and 'l' initialization in your JS)
        k = 187
        key_code = 187
        
        if m >= f:
            # Index past password length: use key char for 'l'
            key_code = ord(key[m])
        elif m >= g:
            # Index past key length: use password char for 'k'
            k = ord(password[m])
        else:
            # Within both lengths: use both
            k = ord(password[m])
            key_code = ord(key[m])
            
        d += dictionary[(k ^ key_code) % h]
        
    return d
