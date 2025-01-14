from app import db
from datetime import datetime
from datetime import timedelta


class Rental(db.Model):
     rental_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
     video_id = db.Column(db.Integer, db.ForeignKey('video.video_id'))
     due_date = db.Column(db.DateTime, nullable=False)
     
     # Need to return a JSON file in the response body
     # This method is only used in the jsonify function
     def to_dict(self):
          format_string = "%Y-%m-%d"  # 2020-06-31
          from app.models.customer import Customer
          from app.models.video import Video
          customer = Customer.read(self.customer_id)
          video = Video.read(self.video_id)
          return {
               "customer_id": self.customer_id,
               "video_id": self.video_id,
               "due_date": self.due_date.strftime(format_string),
               "videos_checked_out_count": customer.videos_checked_out_count,
               "available_inventory": video.available_inventory
          }


     # This method creates a new rental in the database - It associates a customer to a video - 
     # in that association it creates a due date
     @classmethod
     def check_out(cls, customer, video):
          due_date = datetime.utcnow() + timedelta(days=7)
          new_rental = Rental(customer_id=customer.customer_id, video_id=video.video_id, due_date=due_date)
          customer.videos_checked_out_count = customer.videos_checked_out_count + 1
          video.available_inventory = video.available_inventory - 1
          db.session.add(new_rental)
          db.session.commit()
          return new_rental

     # This method deletes a rental in the database  - 
     # It also validates that a relationship between a customer and a video exists in the first place
     @classmethod
     def check_in(cls, customer, video):
          rental = Rental.query.filter(Rental.customer_id==customer.customer_id).filter(Rental.video_id==video.video_id).first()
          if not rental:
               return False
          customer.videos_checked_out_count = customer.videos_checked_out_count - 1
          video.available_inventory = video.available_inventory + 1
          db.session.delete(rental)
          db.session.commit()
          return True
          

     # Querying the database for the rental model where customer id is = to the customer id provided(input)
     # Creates a join query between customer, video and rental
     # Filter by customer id
     @classmethod
     def read_checked_out_by_customer(cls, customer_id):
          from app.models.customer import Customer
          from app.models.video import Video
          rentals = db.session.query(Customer, Video, Rental).join(Customer, Customer.customer_id==Rental.customer_id)\
            .join(Video, Video.video_id==Rental.video_id).filter(Customer.customer_id == customer_id).all()
          return rentals

     # Querying the database for the rental model where customer id is = to the customer id provided(input)
     # This method tells us who checks out a video
     # Creates a join query between customer, video and rental
     # Filters by video id
     @classmethod
     def read_checked_out_by_video(cls, video_id):
          from app.models.customer import Customer
          from app.models.video import Video
          rentals = db.session.query(Customer, Video, Rental).join(Customer, Customer.customer_id==Rental.customer_id)\
            .join(Video, Video.video_id==Rental.video_id).filter(Video.video_id == video_id).all()
          return rentals