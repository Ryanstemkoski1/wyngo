from abc import ABC, abstractmethod
import datetime
from inventories.models import Reservation as ReservationModel, Variant as VariantModel
from accounts.models import User as UserModel


class AbstractReservation(ABC):
    def __init__(self, retailer):
        self._reservation = None
        self._retailer = retailer

    @abstractmethod
    def store(self, reservation):
        pass

    @abstractmethod
    def process(self, reservation):
        pass

    @abstractmethod
    def run(self):
        pass


class Reservation(AbstractReservation):
    def update_or_create_reservation(self, data):
        reservation = ReservationModel.objects.filter(
            origin_id=data.get("origin_id")
        ).first()

        product = VariantModel.objects.get(id=data.get("product"))

        if not reservation:
            user = UserModel.objects.get(id=data.get("user"))
            time_limit = datetime.datetime.now() + datetime.timedelta(minutes=45)
            reservation = ReservationModel.objects.create(
                origin=self._retailer.origin,
                origin_id=data.get("origin_id"),
                status=data.get("status"),
                quantity=data.get("quantity"),
                time_limit=time_limit,
                variant=product,
                user=user,
                version=1,
                total=data.get("total"),
            )

            data = {"reservation": reservation.id, "status": "EXPIRED"}
            from inventories.tasks import update_status_reservation
            update_status_reservation.apply_async(args=(data,), eta=time_limit)

            reservation.reservation_code = "#{:06d}".format(reservation.id)
        else:
            reservation.quantity = data.get("quantity")
            reservation.total = data.get("total")
            reservation.variant = product
            reservation.version += 1

        reservation.save()

        return reservation

    def store(self, reservation):
        self._reservation = reservation

    def remove(self, data):
        reservation = ReservationModel.objects.get(origin_id=data.get("origin_id"))
        reservation.status = "CANCELLED"
        reservation.save()

    def process(self, reservation):
        self.store(reservation)

    def run(self):
        pass
