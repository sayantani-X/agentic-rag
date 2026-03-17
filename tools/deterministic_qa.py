import re
import datetime
from config import client, LLM_MODEL


# -------------------------
# MAIN ENTRY FUNCTION
# -------------------------

def ask_deterministic(query):

    # Step 1: normalize query
    normalized = normalize_deterministic(query)

    q = normalized.lower().strip()

    # -------------------------
    # 2. DATE HANDLING
    # -------------------------
    result = handle_date(q)
    if result:
        return result

    # -------------------------
    # 3. UNIT CONVERSION
    # -------------------------
    result = handle_unit_conversion(q)
    if result:
        return result

    # -------------------------
    # 4. ARITHMETIC
    # -------------------------
    result = handle_arithmetic(q)
    if result:
        return result

    # -------------------------
    # 5. STRING OPERATIONS
    # -------------------------
    result = handle_string_ops(q)
    if result:
        return result

    # -------------------------
    # 6. LOGIC
    # -------------------------
    result = handle_logic(q)
    if result:
        return result

    # -------------------------
    # 7. FALLBACK → LLM
    # -------------------------
    return llm_fallback(query)


# -------------------------
# NORMALIZER (LLM)
# -------------------------

def normalize_deterministic(query):

    prompt = f"""
Convert the query into a structured deterministic format.

Rules:
- Math → use symbols (+, -, *, /)
- Units → standard abbreviations (km, m, kg, etc.)
- Dates → format as "DD Mon YYYY"
- Keep it short and executable
- Do NOT explain

Query:
{query}

Output:
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    except:
        return query


# -------------------------
# DATE HANDLING
# -------------------------

def handle_date(q):

    try:
        match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", q)

        if match:
            day, month, year = match.groups()

            try:
                date = datetime.datetime.strptime(
                    f"{day} {month} {year}", "%d %b %Y"
                )
            except:
                date = datetime.datetime.strptime(
                    f"{day} {month} {year}", "%d %B %Y"
                )

            return date.strftime("%A")

    except:
        pass

    return None


# -------------------------
# UNIT CONVERSION
# -------------------------

def handle_unit_conversion(q):

    try:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(\w+)\s+to\s+(\w+)", q)

        if not match:
            return None

        value, from_u, to_u = match.groups()
        value = float(value)

        conversions = {
            ("km", "m"): 1000,
            ("m", "km"): 0.001,
            ("cm", "m"): 0.01,
            ("m", "cm"): 100,
            ("mile", "km"): 1.609,
            ("km", "mile"): 0.621,
            ("kg", "g"): 1000,
            ("g", "kg"): 0.001,
        }

        key = (from_u, to_u)

        if key in conversions:
            return str(value * conversions[key])

    except:
        pass

    return None


# -------------------------
# ARITHMETIC
# -------------------------

def handle_arithmetic(q):

    try:
        expr = q

        # 🔥 Step 1: convert words → operators
        replacements = {
            "plus": "+",
            "minus": "-",
            "multiplied by": "*",
            "times": "*",
            "into": "*",
            "divide": "/",
            "divided by": "/",
            "over": "/"
        }

        for k, v in replacements.items():
            expr = expr.replace(k, v)

        # 🔥 Step 2: remove extra words like "what do we get if"
        expr = re.sub(r"[a-zA-Z?]", " ", expr)

        # 🔥 Step 3: keep only valid math chars
        expr = re.sub(r"[^0-9+\-*/(). ]", "", expr)

        expr = expr.strip()

        if expr:
            return str(eval(expr))

    except:
        pass

    return None


# -------------------------
# STRING OPERATIONS
# -------------------------

def handle_string_ops(q):

    try:
        if q.startswith("reverse"):
            text = q.replace("reverse", "").strip()
            return text[::-1]

        if q.startswith("uppercase"):
            text = q.replace("uppercase", "").strip()
            return text.upper()

        if q.startswith("lowercase"):
            text = q.replace("lowercase", "").strip()
            return text.lower()

        if "count words" in q:
            return str(len(q.split()))

    except:
        pass

    return None


# -------------------------
# LOGIC
# -------------------------

def handle_logic(q):

    try:
        if "even" in q:
            num = int(re.findall(r"\d+", q)[0])
            return "True" if num % 2 == 0 else "False"

        if "odd" in q:
            num = int(re.findall(r"\d+", q)[0])
            return "True" if num % 2 != 0 else "False"

        if "greater than" in q:
            nums = list(map(int, re.findall(r"\d+", q)))
            if len(nums) == 2:
                return str(nums[0] > nums[1])

    except:
        pass

    return None


# -------------------------
# LLM FALLBACK
# -------------------------

def llm_fallback(query):

    prompt = f"""
You are a precise computation engine.

Solve the query exactly.

Rules:
- Be confident for computable queries
- Return ONLY the final answer
- Do NOT explain unless necessary

Query:
{query}
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"