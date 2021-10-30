from django.db import models
import os
import datetime
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import gettext as _


class Flight(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(verbose_name=_('Date'), default=datetime.datetime.now(tz=timezone.utc))
    site = models.CharField(max_length=32, verbose_name=_('Site'), default='St Hilaire du Touvet')
    duration = models.fields.PositiveSmallIntegerField(verbose_name=_('Durée'), default=0)
    wing = models.CharField(max_length=32, verbose_name=_('Aile'), default='Hook 5P, NIVIUK')
    context = models.CharField(max_length=32, verbose_name=_('Cadre'), default='Autonomie')
    comment = models.CharField(max_length=2048, verbose_name=_('Commentaires'))
    igc = models.FileField(verbose_name=_('Trace IGC'), upload_to='tracks/', blank=True, default='')

    class Meta:
        ordering = ['date']

    
    def igc_filename(self):
        return os.path.basename(self.igc.name)

    def get_images(self):
        images = []
        img_queryset = Image.objects.filter(flight__id=self.id)
        if img_queryset:
            for img in img_queryset:
                images.append(img.to_dictionary())
        return images

    def get_videos(self):
        videos = []
        vid_queryset = Video.objects.filter(flight__id=self.id)
        if vid_queryset:
            for vid in vid_queryset:
                videos.append(vid.to_dictionary())
        return videos

    def to_dictionary(self):
        igc_path = ""
        if self.igc:
            igc_path = self.igc.path

        dictionary = {
            "date": self.date.strftime('%d/%m/%y %H:%M'),
            "site": self.site,
            "duration": self.duration,
            "wing": self.wing,
            "context": self.context,
            "comment": self.comment,
            "igc": igc_path
        }
        
        images = self.get_images()
        if images:
            dictionary["images"] = images

        videos = self.get_videos()
        if videos:
            dictionary["videos"] = videos

        return dictionary


class Image(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    img_path = models.FileField(upload_to='images/', default="")

    def to_dictionary(self):
        return {
            "url": self.img_path.__str__()
        }


class Video(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    video_path = models.FileField(upload_to='videos/', default="")

    def to_dictionary(self):
        return {
            "url": self.video_path.__str__()
        }


# Deletes file from filesystem when corresponding `Image` object is deleted.
@receiver(models.signals.pre_delete, sender=Image)
def delete_img_pre_delete_post(sender, instance, *args, **kwargs):
    if instance.img_path:
        if os.path.isfile(instance.img_path.path):
            os.remove(instance.img_path.path)


# Deletes file from filesystem when corresponding `Videos` object is deleted.
@receiver(models.signals.pre_delete, sender=Video)
def delete_video_pre_delete_post(sender, instance, *args, **kwargs):
    if instance.video_path:
        if os.path.isfile(instance.video_path.path):
            os.remove(instance.video_path.path)


# Deletes file from filesystem when corresponding `igc` object is deleted.
@receiver(models.signals.post_delete, sender=Flight)
def delete_igc_post_delete_post(sender, instance, *args, **kwargs):
    if instance.igc:
        if os.path.isfile(instance.igc.path):
            os.remove(instance.igc.path)

# Deletes file from filesystem when corresponding `igc` object is changed.
@receiver(models.signals.pre_save, sender=Flight)
def auto_delete_igc_on_change_post(sender, instance, **kwargs):
    if instance.pk:
        if Flight.objects.get(pk=instance.pk).igc:
            old_file = Flight.objects.get(pk=instance.pk).igc.path
            if instance.igc:
                new_file = instance.igc.path
                if not old_file == new_file:
                    if os.path.isfile(old_file):
                        os.remove(old_file)
            else:
                # update with no new file => it is indeed a deletion
                if os.path.isfile(old_file):
                    os.remove(old_file)

