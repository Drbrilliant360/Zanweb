from rest_framework import serializers
from .models import DonationCampaign, DonationTier, Donation


class DonationTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationTier
        fields = '__all__'


class DonationCampaignSerializer(serializers.ModelSerializer):
    tiers = DonationTierSerializer(many=True, read_only=True)
    raised_amount = serializers.ReadOnlyField()
    percent_achieved = serializers.ReadOnlyField()

    class Meta:
        model = DonationCampaign
        fields = '__all__'
        read_only_fields = ['raised_amount', 'created_at', 'slug']


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ['status', 'transaction_reference', 'donor', 'created_at', 'completed_at', 'currency']

    def validate(self, data):
        method = data.get('method')
        if method == 'mobile_money':
            if not data.get('donor_phone'):
                raise serializers.ValidationError({
                    'donor_phone': 'Phone number is required for mobile money payments.',
                })
            if not data.get('donor_email'):
                raise serializers.ValidationError({
                    'donor_email': 'Email is required for mobile money payments.',
                })
            amount = data.get('amount')
            if amount is not None and int(amount) < 500:
                raise serializers.ValidationError({
                    'amount': 'Minimum mobile money donation is 500 TZS.',
                })
            data['currency'] = 'TZS'
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['donor'] = request.user
        if validated_data.get('is_anonymous'):
            validated_data['donor_name'] = 'Anonymous'
        return super().create(validated_data)


class ConfirmDonationSerializer(serializers.Serializer):
    transaction_reference = serializers.CharField(max_length=100)
