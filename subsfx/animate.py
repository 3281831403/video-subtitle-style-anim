"""Deterministic pop-in animation primitives for styled subtitles.

Every public function below is an intentional stub: it raises
``NotImplementedError`` so that the acceptance suite starts red.  Implement the
functions without changing their signatures.

Conventions
-----------
* All times are milliseconds; all geometry is in pixels.
* The eight functions are pure and deterministic: no clock reads, no random
  numbers, and no state shared between calls.
* Unless a docstring says otherwise, numerical assertions use an absolute
  tolerance of ``1e-9``.
* Only the Python standard library (``math``) and pytest may be used.
"""


def char_times(text: str, start_ms: float, per_char_ms: float) -> list[float]:
    """Return the appearance time of every character in ``text``.

    Contract
    --------
    * The result is a list of floats with one entry per character, in text
      order.  Character ``i`` appears at exactly ``start_ms + i * per_char_ms``
      (the first character is at ``start_ms``, not one step later).
    * ``per_char_ms`` is the per-character delay and must be non-negative;
      a negative value raises ``ValueError``.  Positive values must produce a
      real stagger.  ``0`` is the explicit simultaneous mode and is allowed.
    * With positive ``per_char_ms`` and non-empty ``text`` the last onset must
      be strictly less than the exclusive timeline
      ``start_ms + per_char_ms * len(text)``.  A 1-based accumulation that puts
      the last character at or beyond that boundary is a bug.
    * Empty text returns ``[]``.  No rounding is allowed; adjacent gaps must be
      equal within the module tolerance of ``1e-9`` ms.
    """
    raise NotImplementedError


def ease_out_back(t: float, overshoot: float) -> float:
    """Evaluate a clamped cubic "back-out" easing curve at normalized time.

    Contract
    --------
    * ``t`` is clamped to ``[0.0, 1.0]``.  The endpoints are exact: the curve
      returns ``0.0`` at ``t=0`` and ``1.0`` at ``t=1`` within ``1e-9``.  There
      must be no initial offset and no leftover overshoot at the end.
    * ``overshoot`` is clamped to the inclusive range ``[0.0, 2.0]`` before it
      is used.  Values outside that range behave exactly like the nearest
      bound.  This clamp is what keeps extreme parameters from driving the
      glyph scale negative.
    * A positive clamped ``overshoot`` produces a spring-like value above
      ``1.0`` before settling back to ``1.0``; the curve is never negative.
      ``overshoot=0`` falls back to a monotone ease-out curve.
    * The result is continuous and deterministic.  Do not use linear
      interpolation; that removes the back/spring feel.
    * Results are compared with an absolute tolerance of ``1e-9``.
    """
    raise NotImplementedError


def scale_at(
    char_time: float,
    now: float,
    dur_ms: float,
    overshoot: float,
) -> float:
    """Return the scale of one glyph at time ``now``.

    Contract
    --------
    * ``dur_ms`` is the glyph's pop duration and must be greater than zero;
      otherwise raise ``ValueError``.
    * Before the character appears (``now <= char_time``) the scale is exactly
      ``0.0``.
    * At the end of the pop (``now >= char_time + dur_ms``) the scale is
      exactly ``1.0``.
    * In between, let ``p = (now - char_time) / dur_ms`` and return
      ``ease_out_back(p, overshoot)``.  Scale therefore follows the same
      back-easing curve, may rise above ``1.0`` briefly, and must never become
      negative after the overshoot clamp.
    * Endpoint values and all comparisons use an absolute tolerance of
      ``1e-9``.
    """
    raise NotImplementedError


def opacity_at(char_time: float, now: float, fade_ms: float) -> float:
    """Return the opacity of one glyph at time ``now``.

    Contract
    --------
    * ``fade_ms`` is the fade-in length and must be non-negative; a negative
      value raises ``ValueError``.
    * Opacity is ``0.0`` at or before ``char_time`` and rises linearly to
      exactly ``1.0`` at ``char_time + fade_ms``; it stays ``1.0`` afterwards.
    * With ``fade_ms == 0`` the transition is an instantaneous step.
    * Only ``fade_ms`` controls the fade endpoint.  It must not be replaced by
      or made to wait for the glyph's scale duration; a short fade can finish
      while the pop is still overshooting.
    * Results are compared with an absolute tolerance of ``1e-9``.
    """
    raise NotImplementedError


def layout_chars(text: str, style: dict) -> list[dict]:
    """Lay out each character and return its left position and advance width.

    ``style`` fields
    ----------------
    * ``font_size`` (required): positive number in pixels.
    * ``letter_spacing`` (optional, default ``0.0``): extra pixels inserted
      between adjacent glyphs, never after the final glyph.
    * ``cjk_ratio`` (optional, default ``1.0``): width of a wide East Asian
      glyph as a fraction of ``font_size``.
    * ``latin_ratio`` (optional, default ``0.5``): width of a half-width glyph
      as a fraction of ``font_size``.

    Contract
    --------
    * Return one dict per character with exactly these keys: ``"char"``,
      ``"index"``, ``"x"`` and ``"width"``.  ``x`` is the left edge; the first
      character starts at ``0.0``.  Each following ``x`` is the previous
      ``x + width + letter_spacing``.
    * CJK characters must use their full, non-monospace advance width:
      ``font_size * cjk_ratio``.  This includes CJK Unified Ideographs and
      Extension A, kana, Hangul syllables, and full-width punctuation based on
      their code-point ranges.  Do not assume every glyph has the same width
      and do not treat CJK as half-width.
    * All other characters use ``font_size * latin_ratio``.
    * The widths and positions must be exact to an absolute tolerance of
      ``1e-9`` pixels.  The final right edge is
      ``last["x"] + last["width"]`` with no trailing letter spacing.
    * Empty text returns ``[]``.  A non-positive ``font_size`` raises
      ``ValueError``.
    """
    raise NotImplementedError


def stroke_width_at(scale: float, base_width: float) -> float:
    """Return the stroke width for a glyph drawn at ``scale``.

    Contract
    --------
    * The stroke width is a style property, not a geometric one: it is always
      ``base_width`` and must not be multiplied, divided, or otherwise
      modulated by ``scale``.
    * This holds at ``scale=0``, at ``scale=1``, during overshoot, and for any
      scale greater than ``1``.  Negative ``base_width`` clamps to ``0.0``.
    * The returned value matches ``base_width`` to an absolute tolerance of
      ``1e-9``.
    """
    raise NotImplementedError


def validate_style(style: dict) -> list[str]:
    """Validate a style/config mapping and return human-readable errors.

    Required numeric fields are ``font_size``, ``per_char_ms``,
    ``char_dur_ms``, ``fade_ms`` and ``overshoot``.  The relationships are:

    * ``font_size > 0``
    * ``per_char_ms >= 0`` and ``per_char_ms <= char_dur_ms`` so the stagger
      stays within one glyph's pop instead of leaving an unanimated gap
    * ``char_dur_ms > 0``
    * ``fade_ms >= 0`` and, critically, ``fade_ms <= char_dur_ms``: a fade
      longer than the pop would still be incomplete when scaling has already
      finished
    * ``overshoot`` in the inclusive range ``[0.0, 2.0]``

    Optional fields, when present, are checked as ``letter_spacing >= 0``,
    ``cjk_ratio > 0`` and ``latin_ratio > 0``.

    Contract
    --------
    * Return ``[]`` for a valid mapping.  Never raise for validation failures.
    * A missing or non-numeric required field yields
      ``"<name> is required and must be a number"``.
    * The exact messages, in output order, are:
      ``"font_size must be > 0"``,
      ``"per_char_ms must be >= 0"``,
      ``"char_dur_ms must be > 0"``,
      ``"fade_ms must be >= 0"``,
      ``"per_char_ms must be <= char_dur_ms"``,
      ``"fade_ms must be <= char_dur_ms"``,
      ``"overshoot must be in [0, 2]"``,
      ``"letter_spacing must be >= 0"``,
      ``"cjk_ratio must be > 0"``,
      ``"latin_ratio must be > 0"``.
    * Report each failing rule once; do not emit duplicate messages.  Unknown
      extra keys are ignored.  Do not mutate ``style``.
    """
    raise NotImplementedError


def anim_batch(clips: list[dict], config: dict) -> dict:
    """Build independent pop-animation schedules for a batch of clips.

    Each clip is a mapping with ``id`` (unique non-empty string), ``text``
    (string) and ``start_ms`` (number).  ``config`` is a style mapping checked
    by :func:`validate_style`; it must also be usable by :func:`layout_chars`.

    Return value
    ------------
    A dict keyed by clip id, in input order::

        {
            "<id>": {
                "id": "<id>",
                "start_ms": <float>,
                "timeline_end_ms": <float>,
                "end_ms": <float>,
                "chars": [
                    {"char": ..., "index": ..., "time_ms": ...,
                     "x": ..., "width": ...},
                    ...
                ],
            },
            ...
        }

    * ``chars`` combines :func:`char_times` and :func:`layout_chars`: it has
      one entry per character with ``time_ms``, ``x`` and ``width``.
    * ``timeline_end_ms`` is the exclusive text boundary
      ``start_ms + per_char_ms * len(text)``; every onset is strictly before
      it for positive ``per_char_ms``.
    * ``end_ms`` is when the final glyph's pop completes:
      ``start_ms + per_char_ms * max(0, len(text) - 1) + char_dur_ms``.
    * Every clip starts from its own ``start_ms``.  Never keep a running
      timeline across clips, because that makes clip two depend on clip one's
      length and text.
    * A batch with several clips must produce exactly the same per-clip
      schedules as running each clip alone through ``anim_batch``.
    * Raise ``ValueError`` when ``validate_style(config)`` reports errors, or
      when a clip id is missing, empty or duplicated.  Do not mutate ``clips``
      or ``config``.  An empty batch returns ``{}``.
    """
    raise NotImplementedError
