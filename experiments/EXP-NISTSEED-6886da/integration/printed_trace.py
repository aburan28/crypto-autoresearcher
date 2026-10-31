"""Supplemental printed tokens from the recovered ECPP source, never hidden state."""
import base64
import re

SOURCE_GRAMMAR = {
    'archive_sha256': '0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f',
    'ECPP/Ecpp/C/c/lfactor.c': '1c12f226fb28eb7814debed5d745b3d7a3fbf0e6ca541830c339358193f3faa5',
    'ECPP/Bigmod/c/bzio.c': '776f8283dead27bef14b4f394fc16239fb6d45bcd59a36babe3a270544a84a11',
    'ECPP/Ecpp/C/c/ecpp.c': '16766d2b73a5424b4252d0d75ba5a4346fae1d908ecc04eb7bca8bf1930071e2',
}
FACTOR = re.compile(rb'% Factor= ([0-9]+)\^(-?[0-9]+)')
DEPTH = re.compile(rb'% D\[\[([0-9]+)\]\]=\s*(-?[0-9]+)')
CHAIN_FIELD = re.compile(rb'% [ABm]\[\[([0-9]+)\]\]=-?[0-9]+')


def extract(raw: bytes) -> dict:
    events = []
    offset = 0
    context = None
    for line in raw.splitlines(keepends=True):
        text = line[:-2] if line.endswith(b'\r\n') else line[:-1] if line.endswith(b'\n') else line
        complete = line.endswith(b'\n')
        d = DEPTH.fullmatch(text)
        if d and complete:
            context = dict(depth=d[1].decode('ascii'), discriminant=d[2].decode('ascii'), offset=offset)
        f = FACTOR.fullmatch(text)
        if f or text.startswith(b'% Factor='):
            event = dict(kind='factor' if f and complete else 'incomplete_or_unrecognized_factor_line',
                         raw_offset=offset, raw_bytes_base64=base64.b64encode(line).decode(),
                         printed=True, complete_line=complete,
                         preceding_printed_discriminant=context.copy() if context else None)
            if f:
                event.update(factor=f[1].decode('ascii'), exponent=f[2].decode('ascii'),
                             arithmetic_shape_valid=int(f[1]) >= 2 and int(f[2]) > 0)
            events.append(event)
        field = CHAIN_FIELD.fullmatch(text)
        compatible_field = bool(field and complete and context and field[1].decode('ascii') == context['depth'])
        if not d and not (f and complete) and not compatible_field:
            context = None
        offset += len(line)
    return dict(schema='crypto.autoresearch.ecpp_printed_factors.v1',
                source_grammar=SOURCE_GRAMMAR, events=events,
                unprinted_state='UNOBSERVED', scope='Printed factor tokens, not all attempted factorizations or primality evidence.')
