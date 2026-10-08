from markupsafe import Markup, escape

from odoo import fields, models
from odoo.tools.misc import formatLang


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def _get_summary_data(self):
        """Regroupe les lignes de 'Correction de valorisation' par produit.

        Retourne :
          - products  : {produit: {'qty', 'original', 'fees': {frais: montant}}}
          - fee_types : la liste des types de frais (une colonne par frais)
        """
        self.ensure_one()
        products = {}
        fee_types = []
        seen_moves = set()

        for line in self.valuation_adjustment_lines:
            product = line.product_id
            fee = line.cost_line_id.product_id
            if fee not in fee_types:
                fee_types.append(fee)

            data = products.setdefault(product, {'qty': 0.0, 'original': 0.0, 'fees': {}})

            # Quantité et valeur d'origine : une seule fois par mouvement de stock
            if line.move_id not in seen_moves:
                seen_moves.add(line.move_id)
                data['qty'] += line.quantity
                data['original'] += line.former_cost

            # Frais : on additionne par type de frais
            data['fees'][fee] = data['fees'].get(fee, 0.0) + line.additional_landed_cost

        return products, fee_types

    summary_html = fields.Html(
        string='Récapitulatif',
        compute='_compute_summary_html',
        sanitize=False,
    )

    def _compute_summary_html(self):
        for cost in self:
            products, fee_types = cost._get_summary_data()
            cost.summary_html = cost._render_summary_table(products, fee_types) if products else False

    def _render_summary_table(self, products, fee_types):
        """Construit le tableau : une ligne par produit, une colonne par type de frais."""
        def money(amount):
            return formatLang(self.env, amount, currency_obj=self.currency_id)

        def row(cells, tag='td'):
            html = f'<{tag}>{escape(cells[0])}</{tag}>'
            html += ''.join(f'<{tag} class="text-end">{escape(c)}</{tag}>' for c in cells[1:])
            return f'<tr>{html}</tr>'

        header = ['Produit', 'Qté', 'Achat / pièce']
        header += [f'{fee.name} / pièce' for fee in fee_types]
        header += ['Coût de revient / pièce', 'Total']

        body = []
        total = {'qty': 0.0, 'original': 0.0, 'fees': dict.fromkeys(fee_types, 0.0)}
        for product, data in products.items():
            qty = data['qty']
            fees = [data['fees'].get(fee, 0.0) for fee in fee_types]
            line_total = data['original'] + sum(fees)

            def per_piece(amount):
                return amount / qty if qty else 0.0

            body.append(row(
                [product.display_name, f"{qty:g}", money(per_piece(data['original']))]
                + [money(per_piece(amount)) for amount in fees]
                + [money(per_piece(line_total)), money(line_total)]
            ))
            total['qty'] += qty
            total['original'] += data['original']
            for fee, amount in zip(fee_types, fees):
                total['fees'][fee] += amount

        grand_total = total['original'] + sum(total['fees'].values())
        head_html = row(header, tag='th')
        foot_html = row(
            ['Total du lot', f"{total['qty']:g}", money(total['original'])]
            + [money(total['fees'][fee]) for fee in fee_types]
            + ['', money(grand_total)],
            tag='th',
        )
        return Markup(
            '<table class="table table-sm table-bordered">'
            f'<thead>{head_html}</thead>'
            f'<tbody>{"".join(body)}</tbody>'
            f'<tfoot>{foot_html}</tfoot>'
            '</table>'
        )
